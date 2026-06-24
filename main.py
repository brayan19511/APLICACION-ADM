import logging
from pathlib import Path
import sys

from PySide6.QtCore import QLockFile, QStandardPaths, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from core.app_info import APP_NAME, APP_VERSION
from core.update_service import UpdateController
from modules.main.presenter import MainPresenter


def configure_logging():
    log_dir = Path.home() / f".{APP_NAME.lower()}"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "adm.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def update_health_file() -> Path | None:
    try:
        index = sys.argv.index("--update-health-file")
        return Path(sys.argv[index + 1])
    except (ValueError, IndexError):
        return None


def acquire_instance_lock() -> QLockFile | None:
    data_dir = Path(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
    )
    data_dir.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(data_dir / "ADM.lock"))
    lock.setStaleLockTime(15_000)
    if lock.tryLock(100):
        return lock
    QMessageBox.warning(
        None,
        "ADM ya está abierto",
        "Ya existe otra instancia de ADM en ejecución. "
        "Ciérrela antes de abrir o actualizar la aplicación.",
    )
    return None


def run():
    configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    instance_lock = acquire_instance_lock()
    if instance_lock is None:
        return 0
    app.instance_lock = instance_lock
    icon = resource_path("assets/favicon.ico")
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    presenter = MainPresenter()
    presenter.run()
    health_file = update_health_file()
    if health_file is not None:
        health_file.parent.mkdir(parents=True, exist_ok=True)
        health_file.write_text(APP_VERSION, encoding="utf-8")

    update_controller = UpdateController(presenter.view)
    presenter.update_controller = update_controller
    QTimer.singleShot(1500, update_controller.check_async)
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
