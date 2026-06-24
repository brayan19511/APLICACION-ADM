class ApplicationError(Exception):
    """Error esperado que puede mostrarse directamente al usuario."""


class ValidationError(ApplicationError):
    """Los datos de entrada no cumplen el contrato requerido."""


class ExportError(ApplicationError):
    """No fue posible generar un archivo de salida."""


class UpdateError(ApplicationError):
    """No fue posible comprobar o instalar una actualización."""
