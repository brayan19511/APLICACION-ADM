from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QAction
from core.app_info import APP_VERSION

class MainView(QMainWindow):
    """Vista principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Aplicación Administración — v{APP_VERSION}")
        self.resize(1000, 650)

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

        menu_structure={
            "Administración":{"gestion_def":"Gestión DEF"}
            ,"Facturación": {"facturacion_comercial": "Masivo Comercial"}
        }
        self.actions = {}
        for menu_name,actions in menu_structure.items():
            menu=menu_bar.addMenu(menu_name)
            for action_key,action_text in actions.items():
                action=QAction(action_text,self)
                menu.addAction(action)
                self.actions[action_key]=action
