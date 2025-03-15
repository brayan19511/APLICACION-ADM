from modules.adm_ncr_def.model import NcrDefProcesor
from modules.adm_ncr_def.view import AdmNcrDefView

class AdmDefPresenter:
    def __init__(self):
        self.model=NcrDefProcesor()
        self.view=AdmNcrDefView()
    def get_view(self):
        return self.view