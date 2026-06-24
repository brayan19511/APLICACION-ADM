
from PySide6.QtWidgets import QWidget, QHBoxLayout

from modules.adm_ncr_def.adm_def_view import AdmDefView
from modules.adm_ncr_def.adm_bcp_view import AdmBCPView


class AdmNcrDefView(QWidget):
    def __init__(self, adm_def_view=None, adm_bcp_view=None):
        super().__init__()
        self.layoutMain = QHBoxLayout()
        self.adm_def_view = adm_def_view or AdmDefView()
        self.adm_bcp_view = adm_bcp_view or AdmBCPView()
        self.layoutMain.addWidget(self.adm_def_view)
        self.layoutMain.addWidget(self.adm_bcp_view)
        self.setLayout(self.layoutMain)
