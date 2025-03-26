

class MainModel:
    """Modelo del módulo principal, almacena el estado."""
    
    def __init__(self):
        self.estado = "Iniciando aplicación"

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def obtener_estado(self):
        return self.estado
