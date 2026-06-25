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
        self._workers = set()
        self.view.source_selected.connect(self.source_selected)
        self.view.load_requested.connect(self.load)
        self.view.export_excel_requested.connect(self.export_excel)
        self.view.export_txt_requested.connect(self.export_txt)

    def get_view(self):
        return self.view

    def _run(self, operation, on_result, invalidate_on_error=False):
        self.view.set_busy(True)
        worker = TaskWorker(operation)
        self._workers.add(worker)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(
            lambda exc, trace: self._show_error(
                exc, trace, invalidate_on_error
            )
        )
        worker.signals.finished.connect(
            lambda current=worker: self._finish_worker(current)
        )
        self.pool.start(worker)

    def _finish_worker(self, worker):
        self.view.set_busy(False)
        self._workers.discard(worker)

    def _show_error(self, exception, trace, invalidate):
        LOGGER.error("Error de procesamiento\n%s", trace)
        if invalidate:
            self.reset_data()
        self.view.show_message(
            str(exception), "Problemas con el archivo", "warning"
        )

    def reset_data(self):
        self.model.df = None
        self.model.path = None
        self.model.cabecera = []
        self.model.detalle = []
        self.view.clear_statistics()
        self.view.set_processed(False)

    def source_selected(self, path):
        self.reset_data()
        self._run(
            lambda: self.model.get_sheet_names(path),
            self.view.show_sheets,
            invalidate_on_error=True,
        )

    def load(self, path, sheet, folio, exchange_rate):
        self.view.clear_statistics()
        self.view.set_processed(False)

        def operation():
            self.model.CargarDataFrame(path, sheet, folio, exchange_rate)
            self.model.ProcesarData()
            self.model.CargaPlantilla()
            return self.model.analizarData()

        self._run(operation, self._loaded, invalidate_on_error=True)

    def _loaded(self, statistics):
        self.view.show_statistics(statistics)
        self.view.set_processed(True)
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
