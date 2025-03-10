from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QStackedWidget

from PySide6.QtGui import QAction  # 🔹 Importar QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicación Administración")
        self.resize(1000,600)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layoutMain = QVBoxLayout(central_widget)
        self.create_menu_bar()

        # contenedor de widgets
        self.stacket_widget=QStackedWidget()
        self.layoutMain.addWidget(self.stacket_widget)
        

        self.setLayout(self.layoutMain)



    def add_pages(self,adm_def_page):
        """Asignamos las páginas a la interfaz"""
        self.stacket_widget.addWidget(adm_def_page)



    def create_menu_bar(self):
        """Crea la barra de menú"""
        menu_bar = self.menuBar()  # 🔹 Obtiene la barra de menú de QMainWindow

        # Menú principal "Gestión"
        gestion_menu = menu_bar.addMenu("Administración")

        # Acción para abrir la vista de Administración DEF
        self.action_home = QAction("Home", self)
        gestion_menu.addAction(self.action_home ) 
        self.action_gestion_def = QAction("Gestión DEF", self)
        gestion_menu.addAction(self.action_gestion_def) 
        self.action_gestion_seller = QAction("Gestión DEF Seller", self)
        gestion_menu.addAction(self.action_gestion_seller) 




