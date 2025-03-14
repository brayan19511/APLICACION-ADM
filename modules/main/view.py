from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QAction

class MainView(QMainWindow):
    """Vista principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicación Administración")
        self.resize(1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layoutMain = QVBoxLayout(central_widget)
        self.create_menu_bar()

        # Contenedor de widgets
        self.stacked_widget = QStackedWidget()
        self.layoutMain.addWidget(self.stacked_widget)

    def create_menu_bar(self):
        """Crea la barra de menú."""
        menu_bar = self.menuBar()
        gestion_menu = menu_bar.addMenu("Administración")

        self.action_home = QAction("Home", self)
        gestion_menu.addAction(self.action_home)

        self.action_gestion_def = QAction("Gestión DEF", self)
        gestion_menu.addAction(self.action_gestion_def)
