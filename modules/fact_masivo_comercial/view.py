from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QFont, QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.view import BaseView
from utils.adm_upload_view import UploadFile


class FacturaMasivoComercialView(BaseView):
    source_selected = Signal(str)
    load_requested = Signal(str, str, int, float)
    export_excel_requested = Signal(str)
    export_txt_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self._busy = False
        self._processed = False
        self.layoutMain = QVBoxLayout()
        title = QLabel("Gestión Facturas Masivo Comercial")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layoutMain.addWidget(title)

        self.upload_file_widget = UploadFile(self.layoutMain)
        self.upload_file_widget.file_selected.connect(self._source_changed)
        self._build_header()
        self._build_buttons()
        self._build_table()
        self._build_log()
        self.setLayout(self.layoutMain)
        self._update_buttons()

    def _build_header(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        self.combo_sheet = QComboBox()
        self.combo_sheet.setFixedWidth(200)
        self.folioTxt = QLineEdit()
        self.folioTxt.setValidator(QIntValidator(1, 2_147_483_647, self))
        self.tcTxt = QLineEdit()
        validator = QDoubleValidator(0.0001, 9999.9999, 4, self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.tcTxt.setValidator(validator)
        self.load_button = QPushButton("Cargar Archivo")
        self.load_button.clicked.connect(self._request_load)

        for widget in (
            QLabel("Seleccione la hoja:"),
            self.combo_sheet,
            QLabel("Siguiente Folio:"),
            self.folioTxt,
            QLabel("T.C:"),
            self.tcTxt,
            self.load_button,
        ):
            layout.addWidget(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layoutMain.addWidget(container)

    def _build_buttons(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        self.excel_button = QPushButton("Generar Excel")
        self.txt_button = QPushButton("Generar TXT")
        self.excel_button.clicked.connect(self._request_excel)
        self.txt_button.clicked.connect(self._request_txt)
        layout.addWidget(self.excel_button)
        layout.addWidget(self.txt_button)
        self.layoutMain.addWidget(container)

    def _build_table(self):
        labels = [
            "Cantidad de filas a revisar",
            "Cantidad de documentos",
            "Cantidad de documentos Soles",
            "Cantidad de documentos Dólares",
            "Monto Total",
            "Monto Total Soles",
            "Monto Total Dólares",
        ]
        self.table = QTableWidget(len(labels), 2)
        self.table.setHorizontalHeaderLabels(["Descripción", "Valor"])
        self.table.verticalHeader().setVisible(False)
        for row, label in enumerate(labels):
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem("0"))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layoutMain.addWidget(self.table, 1)

    def _build_log(self):
        self.statusLog = QTextEdit()
        self.statusLog.setReadOnly(True)
        self.statusLog.setMaximumHeight(100)
        self.layoutMain.addWidget(self.statusLog)

    def _request_load(self):
        try:
            folio = int(self.folioTxt.text())
            exchange_rate = float(self.tcTxt.text().replace(",", "."))
        except ValueError:
            self.show_message(
                "Ingrese un folio y un tipo de cambio válidos.",
                "Datos incompletos",
                "warning",
            )
            return
        self.load_requested.emit(
            self.upload_file_widget.getFile() or "",
            self.combo_sheet.currentText(),
            folio,
            exchange_rate,
        )

    def _request_excel(self):
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
            f"FAC_MASIVO_{stamp}.xlsx",
            "Excel Files (*.xlsx)",
        )
        if path:
            self.export_excel_requested.emit(path)

    def _request_txt(self):
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
            "Nombre base de los TXT",
            f"FAC_MASIVO_{stamp}.txt",
            "Text Files (*.txt)",
        )
        if path:
            self.export_txt_requested.emit(path)

    def _source_changed(self, filepath):
        self.combo_sheet.clear()
        self.clear_statistics()
        self.statusLog.clear()
        self.set_processed(False)
        self.source_selected.emit(filepath)

    def show_sheets(self, sheets):
        self.combo_sheet.clear()
        self.combo_sheet.addItems(sheets)

    def set_busy(self, busy: bool):
        self._busy = busy
        self._update_buttons()

    def set_processed(self, processed: bool):
        self._processed = processed
        self._update_buttons()

    def _update_buttons(self):
        self.upload_file_widget.set_enabled(not self._busy)
        self.load_button.setEnabled(not self._busy)
        enabled_export = not self._busy
        self.excel_button.setEnabled(enabled_export)
        self.txt_button.setEnabled(enabled_export)

    def log_status(self, message):
        self.statusLog.append(message)

    def clear_statistics(self):
        for row in range(7):
            self.table.setItem(row, 1, QTableWidgetItem("0"))

    def show_statistics(self, values):
        review, docs, pen_docs, usd_docs, total, pen_total, usd_total = values
        formatted = [
            f"{review}",
            f"{docs}",
            f"{pen_docs}",
            f"{usd_docs}",
            f"{total:,.2f}",
            f"S/ {pen_total:,.2f}",
            f"US$ {usd_total:,.2f}",
        ]
        for row, value in enumerate(formatted):
            self.table.setItem(row, 1, QTableWidgetItem(value))
