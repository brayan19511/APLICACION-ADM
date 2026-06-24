import logging

from PySide6.QtCore import QThreadPool

from core.worker import TaskWorker
from modules.adm_ncr_def.adm_bcp_view import AdmBCPView
from modules.adm_ncr_def.adm_def_view import AdmDefView
from modules.adm_ncr_def.model import NcrBCPProcesor, NcrDefProcesor
from modules.adm_ncr_def.view import AdmNcrDefView


LOGGER = logging.getLogger(__name__)


class AdmDefPresenter:
    def __init__(self):
        self.def_model = NcrDefProcesor()
        self.bcp_model = NcrBCPProcesor()
        self.def_view = AdmDefView()
        self.bcp_view = AdmBCPView()
        self.view = AdmNcrDefView(self.def_view, self.bcp_view)
        self.pool = QThreadPool.globalInstance()

        self.def_view.load_requested.connect(self.load_def)
        self.def_view.export_requested.connect(self.export_def)
        self.bcp_view.load_requested.connect(self.load_bcp)
        self.bcp_view.export_requested.connect(self.export_bcp)

    def get_view(self):
        return self.view

    def _run(self, view, operation, on_result):
        view.set_busy(True)
        worker = TaskWorker(operation)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(lambda exc, trace: self._show_error(view, exc, trace))
        worker.signals.finished.connect(lambda: view.set_busy(False))
        self.pool.start(worker)

    def _show_error(self, view, exception, trace):
        LOGGER.error("Error de procesamiento\n%s", trace)
        view.clear_statistics()
        view.show_message(str(exception), "Problemas con el archivo", "warning")

    def load_def(self, path):
        def operation():
            self.def_model.CargarDataFrame(path)
            self.def_model.procesarDEF()
            return self.def_model.analizar_dataframe_def()

        self._run(self.def_view, operation, self.def_view.show_statistics)

    def export_def(self, path):
        self._run(
            self.def_view,
            lambda: self.def_model.ExportarDataFrame_def(path),
            lambda message: self.def_view.show_message(message, "Exportación"),
        )

    def load_bcp(self, path):
        def operation():
            self.bcp_model.CargarDataFrame(path)
            self.bcp_model.procesarBCP()
            return self.bcp_model.analizar_dataframe_BCP()

        self._run(self.bcp_view, operation, self.bcp_view.show_statistics)

    def export_bcp(self, path):
        self._run(
            self.bcp_view,
            lambda: self.bcp_model.ExportarDataFrame_bcp(path),
            lambda message: self.bcp_view.show_message(message, "Exportación"),
        )
