
from PySide6.QtWidgets import QWidget,QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog

from modules.adm_ncr_def.adm_def_view import AdmDefView


class AdmNcrDefView(QWidget):
    def __init__(self):
        super().__init__()
        self.layoutMain=QHBoxLayout()
        adm_def_view=AdmDefView()
        self.layoutMain.addWidget(adm_def_view)
        
        self.setLayout(self.layoutMain)
        #   añadir 2 modulos de def