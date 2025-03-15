from core.presenter import BasePresenter
from modules.main.model import MainModel
from modules.main.view import MainView
# from modules.adm_def.view import ContainerDefView
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from modules.adm_ncr_def.presenter import AdmDefPresenter


class MainPresenter(BasePresenter):
    """Presentador del módulo principal, gestiona la lógica."""

    def __init__(self):
        super().__init__(MainModel(), MainView())

        # inicializamos pagina
        self.amd_ncr_def=AdmDefPresenter()

        # Diccionario de vistas
        self.views = {
            "gestion_def":self.amd_ncr_def.get_view(),
            # "home": home_label,
        }

        # Agregar las páginas al stacked_widget
        for view in self.views.values():
            self.view.stacked_widget.addWidget(view)

        # Configurar navegación
        self.view.action_gestion_def.triggered.connect(lambda: self.show_page("gestion_def"))

    def show_page(self, page_name):
        """Muestra la página seleccionada."""
        self.view.stacked_widget.setCurrentWidget(self.views[page_name])

    def run(self):
        """Muestra la ventana principal."""
        self.view.show()
