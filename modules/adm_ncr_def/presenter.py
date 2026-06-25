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
        self._workers = set()

        self.def_view.load_requested.connect(self.load_def)
        self.def_view.export_requested.connect(self.export_def)
        self.bcp_view.load_requested.connect(self.load_bcp)
        self.bcp_view.export_requested.connect(self.export_bcp)
        self.def_view.upload_file_widget.file_selected.connect(self.reset_def)
        self.bcp_view.upload_file_widget.file_selected.connect(self.reset_bcp)

    def get_view(self):
        return self.view

    def _run(self, view, operation, on_result, invalidate_on_error=False):
        view.set_busy(True)
        worker = TaskWorker(operation)
        self._workers.add(worker)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(
            lambda exc, trace: self._show_error(
                view, exc, trace, invalidate_on_error
            )
        )
        worker.signals.finished.connect(
            lambda current=worker: self._finish_worker(view, current)
        )
        self.pool.start(worker)

    def _finish_worker(self, view, worker):
        view.set_busy(False)
        self._workers.discard(worker)

    def _show_error(self, view, exception, trace, invalidate):
        LOGGER.error("Error de procesamiento\n%s", trace)
        if invalidate:
            view.clear_statistics()
            view.set_processed(False)
        view.show_message(str(exception), "Problemas con el archivo", "warning")

    def reset_def(self, _path=None):
        self.def_model.df = None
        self.def_model.path = None
        self.def_view.clear_statistics()
        self.def_view.set_processed(False)

    def reset_bcp(self, _path=None):
        self.bcp_model.df = None
        self.bcp_model.df_bcp = None
        self.bcp_model.path = None
        self.bcp_view.clear_statistics()
        self.bcp_view.set_processed(False)

    def load_def(self, path):
        def operation():
            self.def_model.CargarDataFrame(path)
            self.def_model.procesarDEF()
            return self.def_model.analizar_dataframe_def()

        self.def_view.clear_statistics()
        self.def_view.set_processed(False)
        self._run(
            self.def_view,
            operation,
            self._def_loaded,
            invalidate_on_error=True,
        )

    def _def_loaded(self, statistics):
        self.def_view.show_statistics(statistics)
        self.def_view.set_processed(True)

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

        self.bcp_view.clear_statistics()
        self.bcp_view.set_processed(False)
        self._run(
            self.bcp_view,
            operation,
            self._bcp_loaded,
            invalidate_on_error=True,
        )

    def _bcp_loaded(self, statistics):
        self.bcp_view.show_statistics(statistics)
        self.bcp_view.set_processed(True)

    def export_bcp(self, path):
        self._run(
            self.bcp_view,
            lambda: self.bcp_model.ExportarDataFrame_bcp(path),
            lambda message: self.bcp_view.show_message(message, "Exportación"),
        )
