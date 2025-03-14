from core.presenter import BasePresenter
from modules.main.model import MainModel
from modules.main.view import MainView
# from modules.adm_def.view import ContainerDefView
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class MainPresenter(BasePresenter):
    """Presentador del módulo principal, gestiona la lógica."""

    def __init__(self):
        self.model = MainModel()
        self.view = MainView()
        super().__init__(self.model, self.view)

        # Página principal con un QLabel
        home_label = QLabel("Bienvenido a la página principal")
        home_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        home_label.setFont(QFont("Arial", 16, QFont.Bold))

        # Diccionario de vistas
        self.views = {
            # "gestion_def": ContainerDefView(),
            "home": home_label,
        }

        # Agregar las páginas al stacked_widget
        for view in self.views.values():
            self.view.stacked_widget.addWidget(view)

        # Configurar navegación
        self.view.action_home.triggered.connect(lambda: self.show_page("home"))
        self.view.action_gestion_def.triggered.connect(lambda: self.show_page("gestion_def"))

    def show_page(self, page_name):
        """Muestra la página seleccionada."""
        self.view.stacked_widget.setCurrentWidget(self.views[page_name])

    def run(self):
        """Muestra la ventana principal."""
        self.view.show()
