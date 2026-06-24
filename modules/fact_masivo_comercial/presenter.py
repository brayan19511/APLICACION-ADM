import logging

from PySide6.QtCore import QThreadPool

from core.presenter import BasePresenter
from core.worker import TaskWorker
from modules.fact_masivo_comercial.model import ProcesarComercial
from modules.fact_masivo_comercial.view import FacturaMasivoComercialView


LOGGER = logging.getLogger(__name__)


class FacturasMasivoComercialPresenter(BasePresenter):
    def __init__(self):
        super().__init__(ProcesarComercial(), FacturaMasivoComercialView())
        self.pool = QThreadPool.globalInstance()
        self.view.load_requested.connect(self.load)
        self.view.export_excel_requested.connect(self.export_excel)
        self.view.export_txt_requested.connect(self.export_txt)

    def get_view(self):
        return self.view

    def _run(self, operation, on_result):
        self.view.set_busy(True)
        worker = TaskWorker(operation)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(self._show_error)
        worker.signals.finished.connect(lambda: self.view.set_busy(False))
        self.pool.start(worker)

    def _show_error(self, exception, trace):
        LOGGER.error("Error de procesamiento\n%s", trace)
        self.view.clear_statistics()
        self.view.show_message(
            str(exception), "Problemas con el archivo", "warning"
        )

    def load(self, path, sheet, folio, exchange_rate):
        def operation():
            self.model.CargarDataFrame(path, sheet, folio, exchange_rate)
            self.model.ProcesarData()
            self.model.CargaPlantilla()
            return self.model.analizarData()

        self._run(operation, self._loaded)

    def _loaded(self, statistics):
        self.view.show_statistics(statistics)
        self.view.log_status("Archivo procesado correctamente.")

    def export_excel(self, path):
        self._run(
            lambda: self.model.exportData(path),
            lambda message: self.view.show_message(message, "Exportación"),
        )

    def export_txt(self, path):
        self._run(
            lambda: self.model.exportTxt(path),
            lambda message: self.view.show_message(message, "Exportación"),
        )
