
from core.presenter import BasePresenter
from modules.fact_masivo_comercial.model import ProcesarComercial
from modules.fact_masivo_comercial.view import FacturaMasivoComercialView

class FacturasMasivoComercialPresenter(BasePresenter):
    def __init__(self):
        super().__init__(ProcesarComercial(), FacturaMasivoComercialView())
    def get_view(self):
        return self.view