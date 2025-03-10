
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QMessageBox,QTableWidget,QTableWidgetItem,QHeaderView
from  controllers.adm_def_controller import AdministracionDefController

from views.adm_def.adm_ncr_widget import AdmDefWifget
from views.adm_def.adm_bcp_widget import AdmBCPWifget


# from views.adm_def.progressBarWidget  import ProgressBarWidget

# Pantalla contenedora de widgets
class ContainerDefView(QWidget):
    def __init__(self):
        super().__init__()
        self.adm_def_controller=AdministracionDefController(self)
        self.layout_Main=QHBoxLayout()

        # self.def_plantilla_Widget()
        
        defWidget=AdmDefWifget()
        self.layout_Main.addWidget(defWidget,1)
        bcpWidget=AdmBCPWifget()
        self.layout_Main.addWidget(bcpWidget,1)

        self.setLayout(self.layout_Main)



