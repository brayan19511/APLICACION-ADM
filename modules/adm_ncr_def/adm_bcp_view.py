from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.view import BaseView
from utils.adm_upload_view import UploadFile


class AdmBCPView(BaseView):
    load_requested = Signal(str)
    export_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self._busy = False
        self._processed = False
        self.layout_Main = QVBoxLayout()
        title = QLabel("Generación Plantilla BCP")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout_Main.addWidget(title)
        self._build_content()
        self.setLayout(self.layout_Main)

    def _build_content(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        self.upload_file_widget = UploadFile(layouWidget=layout)

        buttons = QWidget()
        button_layout = QHBoxLayout(buttons)
        self.load_button = QPushButton("Cargar Archivo")
        self.export_button = QPushButton("Exportar")
        self.load_button.clicked.connect(self._request_load)
        self.export_button.clicked.connect(self._request_export)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.export_button)
        layout.addWidget(buttons)

        self.table = QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["Descripción", "Valor"])
        self.table.verticalHeader().setVisible(False)
        labels = [
            "Cantidad de documentos",
            "Monto total",
            "Cantidad de filas a revisar",
            "Monto total a revisar",
            "N° de filas mayor a S/1,500",
        ]
        for row, label in enumerate(labels):
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem("0"))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)
        self.layout_Main.addWidget(container, 1)
        self._update_buttons()

    def _request_load(self):
        self.load_requested.emit(self.upload_file_widget.getFile() or "")

    def _request_export(self):
        if not self._processed:
            self.show_message(
                "Primero debe cargar y procesar un archivo.",
                "Sin datos para exportar",
                "warning",
            )
            return
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo",
            f"BCP_PLANTILLA_{stamp}.xlsx",
            "Excel Files (*.xlsx)",
        )
        if path:
            self.export_requested.emit(path)

    def set_busy(self, busy: bool):
        self._busy = busy
        self._update_buttons()

    def set_processed(self, processed: bool):
        self._processed = processed
        self._update_buttons()

    def _update_buttons(self):
        self.upload_file_widget.set_enabled(not self._busy)
        self.load_button.setEnabled(not self._busy)
        self.export_button.setEnabled(not self._busy)

    def show_statistics(self, values):
        count, amount, review_count, review_amount, unusual = values
        formatted = [
            f"{count}",
            f"S/ {amount:,.2f}",
            f"{review_count}",
            f"S/ {review_amount:,.2f}",
            f"{unusual}",
        ]
        for row, value in enumerate(formatted):
            self.table.setItem(row, 1, QTableWidgetItem(value))

    def clear_statistics(self):
        for row in range(5):
            self.table.setItem(row, 1, QTableWidgetItem("0"))
