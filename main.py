import logging
from pathlib import Path
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

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


def run():
    configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    icon = resource_path("assets/favicon.ico")
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    presenter = MainPresenter()
    presenter.run()

    update_controller = UpdateController(presenter.view)
    presenter.update_controller = update_controller
    QTimer.singleShot(1500, update_controller.check_async)
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
