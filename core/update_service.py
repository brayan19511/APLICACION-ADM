from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

import requests
from packaging.version import InvalidVersion, Version
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from core.app_info import APP_NAME, APP_VERSION
from core.exceptions import UpdateError


LOGGER = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"


@dataclass(frozen=True)
class UpdateSettings:
    repository: str = os.getenv(
        "UPDATE_REPOSITORY", "brayan19511/APLICACION-ADM"
    )
    asset_name: str = os.getenv("UPDATE_ASSET_NAME", "ADM.exe")
    enabled: bool = os.getenv("UPDATE_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    timeout: int = 20


@dataclass(frozen=True)
class ReleaseInfo:
    version: Version
    tag: str
    download_url: str
    expected_sha256: str
    notes: str


class GitHubReleaseUpdater:
    def __init__(self, settings: UpdateSettings | None = None):
        self.settings = settings or UpdateSettings()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "User-Agent": f"{APP_NAME}-Updater/{APP_VERSION}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def check(self) -> ReleaseInfo | None:
        if not self.settings.enabled:
            return None
        url = f"{GITHUB_API}/repos/{self.settings.repository}/releases/latest"
        try:
            response = self.session.get(url, timeout=self.settings.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise UpdateError(f"No se pudo consultar GitHub Releases: {exc}") from exc

        tag = str(payload.get("tag_name", "")).strip()
        try:
            remote_version = Version(tag.lstrip("vV"))
            local_version = Version(APP_VERSION)
        except InvalidVersion as exc:
            raise UpdateError(f"La versión publicada '{tag}' no es válida.") from exc
        if remote_version <= local_version:
            return None

        assets = payload.get("assets") or []
        executable = next(
            (asset for asset in assets if asset.get("name") == self.settings.asset_name),
            None,
        )
        if not executable:
            raise UpdateError(
                f"La versión {tag} no contiene el archivo "
                f"'{self.settings.asset_name}'."
            )
        expected_hash = self._asset_digest(executable, assets)
        return ReleaseInfo(
            version=remote_version,
            tag=tag,
            download_url=executable["browser_download_url"],
            expected_sha256=expected_hash,
            notes=str(payload.get("body") or "").strip(),
        )

    def _asset_digest(self, executable: dict, assets: list[dict]) -> str:
        digest = str(executable.get("digest") or "")
        if digest.lower().startswith("sha256:"):
            return digest.split(":", 1)[1].strip().lower()

        checksum_name = f"{self.settings.asset_name}.sha256"
        checksum_asset = next(
            (asset for asset in assets if asset.get("name") == checksum_name),
            None,
        )
        if checksum_asset:
            try:
                response = self.session.get(
                    checksum_asset["browser_download_url"],
                    timeout=self.settings.timeout,
                )
                response.raise_for_status()
                checksum = response.text.strip().split()[0].lower()
                if len(checksum) == 64:
                    return checksum
            except requests.RequestException as exc:
                raise UpdateError(
                    "No se pudo descargar el checksum de la actualización."
                ) from exc
        raise UpdateError(
            f"La versión debe incluir el digest SHA-256 de GitHub o el asset "
            f"'{checksum_name}'."
        )

    def download(self, release: ReleaseInfo) -> Path:
        update_dir = (
            Path(os.getenv("LOCALAPPDATA", tempfile.gettempdir()))
            / APP_NAME
            / "updates"
        )
        update_dir.mkdir(parents=True, exist_ok=True)
        destination = update_dir / f"{APP_NAME}-{release.version}.exe"
        temporary = destination.with_suffix(".download")
        digest = hashlib.sha256()
        try:
            with self.session.get(
                release.download_url, stream=True, timeout=self.settings.timeout
            ) as response:
                response.raise_for_status()
                with temporary.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output.write(chunk)
                            digest.update(chunk)
            if digest.hexdigest().lower() != release.expected_sha256.lower():
                temporary.unlink(missing_ok=True)
                raise UpdateError(
                    "El archivo descargado no coincide con su hash SHA-256."
                )
            temporary.replace(destination)
            return destination
        except requests.RequestException as exc:
            temporary.unlink(missing_ok=True)
            raise UpdateError(f"No se pudo descargar la actualización: {exc}") from exc

    def schedule_install(self, downloaded_executable: Path) -> None:
        if not getattr(sys, "frozen", False):
            raise UpdateError(
                "El reemplazo automático solo está disponible en el ejecutable empaquetado."
            )
        target = Path(sys.executable).resolve()
        helper = downloaded_executable.with_name("install_update.ps1")
        health_file = downloaded_executable.with_name("startup-ok.txt")
        health_file.unlink(missing_ok=True)
        helper.write_text(
            """param(
    [Parameter(Mandatory=$true)][int]$PidToWait,
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Target,
    [Parameter(Mandatory=$true)][string]$HealthFile
)
$ErrorActionPreference = "Stop"
$Backup = "$Target.bak"
try {
    Wait-Process -Id $PidToWait -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    if (Test-Path -LiteralPath $Backup) {
        Remove-Item -LiteralPath $Backup -Force
    }
    if (Test-Path -LiteralPath $Target) {
        Move-Item -LiteralPath $Target -Destination $Backup -Force
    }
    Move-Item -LiteralPath $Source -Destination $Target -Force
    $NewProcess = Start-Process -FilePath $Target -ArgumentList @("--update-health-file", $HealthFile) -PassThru
    $Healthy = $false
    for ($Attempt = 0; $Attempt -lt 60; $Attempt++) {
        Start-Sleep -Milliseconds 500
        if (Test-Path -LiteralPath $HealthFile) {
            $Healthy = $true
            break
        }
        if ($NewProcess.HasExited) {
            break
        }
        $NewProcess.Refresh()
    }
    if (-not $Healthy) {
        if (-not $NewProcess.HasExited) {
            Stop-Process -Id $NewProcess.Id -Force -ErrorAction SilentlyContinue
        }
        Remove-Item -LiteralPath $Target -Force -ErrorAction SilentlyContinue
        if (Test-Path -LiteralPath $Backup) {
            Move-Item -LiteralPath $Backup -Destination $Target -Force
        }
        Start-Process -FilePath $Target
        throw "La versión nueva no confirmó un inicio correcto."
    }
    if (Test-Path -LiteralPath $Backup) {
        Remove-Item -LiteralPath $Backup -Force
    }
}
catch {
    if ((Test-Path -LiteralPath $Backup) -and -not (Test-Path -LiteralPath $Target)) {
        Move-Item -LiteralPath $Backup -Destination $Target -Force
    }
    if (Test-Path -LiteralPath $Target) {
        Start-Process -FilePath $Target
    }
}
finally {
    Remove-Item -LiteralPath $HealthFile -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $MyInvocation.MyCommand.Path -Force -ErrorAction SilentlyContinue
}
""",
            encoding="utf-8-sig",
        )
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(helper),
                "-PidToWait",
                str(os.getpid()),
                "-Source",
                str(downloaded_executable),
                "-Target",
                str(target),
                "-HealthFile",
                str(health_file),
            ],
            creationflags=creation_flags,
            close_fds=True,
        )


class UpdateController(QObject):
    update_found = Signal(object)
    check_failed = Signal(str)
    download_finished = Signal(object)
    download_failed = Signal(str)

    def __init__(self, parent_window: QWidget):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.updater = GitHubReleaseUpdater()
        self.update_found.connect(self._offer_update)
        self.check_failed.connect(
            lambda message: LOGGER.warning("Actualización no disponible: %s", message)
        )
        self.download_finished.connect(self._install)
        self.download_failed.connect(self._show_download_error)

    def check_async(self):
        if not getattr(sys, "frozen", False) or not self.updater.settings.enabled:
            return

        def check():
            try:
                release = self.updater.check()
                if release:
                    self.update_found.emit(release)
            except UpdateError as exc:
                self.check_failed.emit(str(exc))

        threading.Thread(target=check, daemon=True).start()

    def _offer_update(self, release: ReleaseInfo):
        notes = f"\n\n{release.notes[:800]}" if release.notes else ""
        answer = QMessageBox.question(
            self.parent_window,
            "Actualización disponible",
            f"Está disponible la versión {release.version}. "
            f"Actualmente usa la {APP_VERSION}.{notes}\n\n"
            "¿Desea descargarla e instalarla ahora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        def download():
            try:
                self.download_finished.emit(self.updater.download(release))
            except UpdateError as exc:
                self.download_failed.emit(str(exc))

        threading.Thread(target=download, daemon=True).start()

    def _install(self, executable: Path):
        try:
            self.updater.schedule_install(executable)
        except UpdateError as exc:
            self._show_download_error(str(exc))
            return
        QMessageBox.information(
            self.parent_window,
            "Actualización descargada",
            "La aplicación se cerrará, instalará la nueva versión y volverá a abrirse.",
        )
        QApplication.quit()

    def _show_download_error(self, message: str):
        QMessageBox.warning(
            self.parent_window, "No se pudo actualizar", message
        )
