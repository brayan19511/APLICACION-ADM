class BasePresenter:
    """Clase base para los presentadores en el patrón MVP."""
    def __init__(self,model,view):
        self.model=model
        self.view=view
        