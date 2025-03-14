from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from views.main_widow import MainWindow

from views.adm_def.adm_def_view import ContainerDefView


class MainController:
    def __init__(self):
        # creacion de ventana principal
        self.main_window=MainWindow()
        home_label = QLabel("Bienvenido a la página principal")
        home_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        home_label.setFont(QFont("Arial", 16, QFont.Bold))  
        # home_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.views = {

            "gestion_def": ContainerDefView(),
            "home": home_label,
        }
        # agregamos las paginas
        for view in self.views.values():
            self.main_window.stacket_widget.addWidget(view)
   

        #configuramos navegacion 
        self.main_window.action_home.triggered.connect(lambda: self.show_page("home"))
        self.main_window.action_gestion_def.triggered.connect(lambda: self.show_page("gestion_def"))



    def show_page(self,page_name):
        self.main_window.stacket_widget.setCurrentWidget(self.views[page_name])


    def run(self):
        self.main_window.show()
