from PySide6.QtWidgets import QWidget,QMessageBox 

class BaseView(QWidget):
    """Clase base para las vistas en el patrón MVP."""
    def __init__(self):
        super().__init__()

    def show_message(self, message, title="Información", msg_type="info"):
        """Muestra un QMessageBox genérico."""
        msg_box = QMessageBox(self)

        if msg_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "error":
            msg_box.setIcon(QMessageBox.Critical)

        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()