from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar

class ProgressBarWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layoutMain = QVBoxLayout(self)

        # 🔹 Crear barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)  # Inicialmente en 0%

        self.layoutMain.addWidget(self.progress_bar)

    def update_progress(self, value):
        """Actualizar la barra de progreso"""
        self.progress_bar.setValue(value)
