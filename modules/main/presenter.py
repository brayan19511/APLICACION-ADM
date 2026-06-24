from core.presenter import BasePresenter
from modules.main.model import MainModel
from modules.main.view import MainView
from modules.adm_ncr_def.presenter import AdmDefPresenter
from modules.fact_masivo_comercial.presenter import FacturasMasivoComercialPresenter


class MainPresenter(BasePresenter):
    """Presentador del módulo principal, gestiona la lógica."""

    def __init__(self):
        super().__init__(MainModel(), MainView())

        # inicializamos pagina
        self.amd_ncr_def=AdmDefPresenter()
        self.fact_comercial=FacturasMasivoComercialPresenter()

        # Diccionario de vistas
        self.views = {
            "facturacion_comercial":self.fact_comercial.get_view(),
            "gestion_def":self.amd_ncr_def.get_view(),
        }

        # Agregar las páginas al stacked_widget
        for view in self.views.values():
            self.view.stacked_widget.addWidget(view)
        # Diccionario de navegacion
        for key in self.views.keys():
            self.view.actions[key].triggered.connect(lambda checke,k=key: self.show_page(k))

    def show_page(self, page_name):
        """Muestra la página seleccionada."""
        self.view.stacked_widget.setCurrentWidget(self.views[page_name])

    def run(self):
        """Muestra la ventana principal."""
        self.view.show()
