
from PySide6.QtWidgets import QWidget,QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog

from modules.adm_ncr_def.adm_def_view import AdmDefView
from modules.adm_ncr_def.adm_bcp_view import AdmBCPView


class AdmNcrDefView(QWidget):
    def __init__(self):
        super().__init__()
        self.layoutMain=QHBoxLayout()
        adm_def_view=AdmDefView()
        adm_bcp_view=AdmBCPView()
        self.layoutMain.addWidget(adm_def_view)
        self.layoutMain.addWidget(adm_bcp_view)
        
        self.setLayout(self.layoutMain)
        #   añadir 2 modulos de def