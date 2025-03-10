from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from utils.adm_upload_view import UploadFile
from controllers.adm_def_controller import AdministracionDefController


class AdmDefWifget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout_Main = QVBoxLayout()
        self.adm_def_controller = AdministracionDefController(self)
        titulo = QLabel("Revisión DEF")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # Centrar texto
        titulo.setFont(QFont("Arial", 16, QFont.Bold))

        self.layout_Main.addWidget(titulo)

        self.def_plantilla_Widget()
        self.setLayout(self.layout_Main)

    # definimos 2 pantallas left
    def def_plantilla_Widget(self):
        def_Widget = QWidget()
        layout_widget = QVBoxLayout(def_Widget)

        self.upload_file_widget = UploadFile(layouWidget=layout_widget)

        self.buttons_plantillaWidget(layout_widget)

        # Tabla para mostrar los valores
        self.table = QTableWidget()
        self.table.setRowCount(5)  # 4 estadísticas a mostrar
        self.table.setColumnCount(2)  # 2 columnas (Descripción y Valor)
        self.table.setHorizontalHeaderLabels(["Descripción", "Valor"])
        self.table.verticalHeader().setVisible(False)  # Ocultar índices de fila

        labels = [
            "Cantidad de documentos",
            "Monto total",
            "Cantidad de filas a revisar",
            "Monto total a revisar",
            "N° de filas mayor a S/1,500",
        ]
        for row, label in enumerate(labels):
            self.table.setItem(row, 0, QTableWidgetItem(label))  # Columna 0 (Texto)
            self.table.setItem(row, 1, QTableWidgetItem("0"))  # Columna 1 (Valores)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout_widget.addWidget(self.table)

        self.layout_Main.addWidget(def_Widget, 1)

    def buttons_plantillaWidget(self, widget: QVBoxLayout):
        buttonWidget = QWidget()
        layoutButton = QHBoxLayout(buttonWidget)
        button1 = QPushButton("Cargar Archivo")
        button1.clicked.connect(self.CargarArchivo)
        button2 = QPushButton("Exportar")
        button2.clicked.connect(self.ExportarArchivo)
        layoutButton.addWidget(button1)
        layoutButton.addWidget(button2)
        widget.addWidget(buttonWidget)

    def CargarArchivo(self):
        try:
            self.adm_def_controller.CargarDataFrame(self.upload_file_widget.getFile())
            self.adm_def_controller.validate_columns_DEF()
            self.cargarTable()
        except ValueError as e:
            self.limpiarTable()
            # self.upload_file_widget.Clean()
            # self.adm_def_controller.
            self.mostrarMensaje(
                "Problemas procesando y exportando datos", str(e), "error"
            )
            print(f"Problemas procesando y exportando datos {e}")

    def ExportarArchivo(self):
        try:
            if (
                self.upload_file_widget.getFile()
                != self.adm_def_controller.getFilePath()
            ):
                self.mostrarMensaje(
                    "Advertencia",
                    "Porfavor Cargue el archivo antes de exportar",
                    "error",
                )
                return
            message = self.adm_def_controller.ExportarDataFrame_def("NCR_DEF")
            self.mostrarMensaje("Exportación", message)

        except Exception as e:
            self.mostrarMensaje("Problemas Exportando datos", str(e), "error")
            print(f"Problemas Exportando datos {e}")

    def cargarTable(self):
        num_filas, monto_filas, num_filas_rev, monto_filas_rev, num_filas_atipicos = (
            self.adm_def_controller.analizar_dataframe_def()
        )
        valores = [
            f"{num_filas}",
            f"S/ {monto_filas:,.2f}",
            f"{num_filas_rev}",
            f"S/ {monto_filas_rev:,.2f}",
            f"{num_filas_atipicos}",
        ]
        for row, value in enumerate(valores):
            self.table.setItem(row, 1, QTableWidgetItem(f"{value}"))

    def mostrarMensaje(self, titulo, mensaje, tipo="info"):
        """Muestra un mensaje en pantalla."""
        if tipo == "info":
            QMessageBox.information(self, titulo, mensaje)
        elif tipo == "error":
            QMessageBox.warning(self, titulo, mensaje)

    def limpiarTable(self):
        for row in range(4):
            self.table.setItem(row, 1, QTableWidgetItem("0"))
