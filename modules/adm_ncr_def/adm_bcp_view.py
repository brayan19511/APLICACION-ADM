from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from utils.adm_upload_view import UploadFile
from modules.adm_ncr_def.model import NcrBCPProcesor
from core.view import BaseView


class AdmBCPView(BaseView):

    def __init__(self):
        super().__init__()
        self.layout_Main = QVBoxLayout()
        # self.adm_def_controller = AdministracionDefController(self)
        self.procesor=NcrBCPProcesor()
        titulo = QLabel("Generación Plantilla BCP")
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
            self.procesor.CargarDataFrame(self.upload_file_widget.getFile())
            self.procesor.validate_columns_BCP()
            self.procesor.procesarBCP()
            self.cargarTable()
            pass
        except ValueError as e:
            self.limpiarTable()
            self.show_message(str(e),"Problemas con el archivo","warning")
        except FileNotFoundError as e:  # ✅ Manejo de archivos inexistentes
            self.limpiarTable()
            self.show_message(str(e), "Archivo no encontrado", "error")

    def ExportarArchivo(self):
        """Abre QFileDialog y llama al modelo para exportar"""
        fecha_actual = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", f"BCP_PLANTILLA_{fecha_actual}.xlsx", "Excel Files (*.xlsx)")
        try:

            if(self.upload_file_widget.getFile()!= self.procesor.getFilePath()):
                self.show_message("Porfavor Cargue el archivo antes de exportar", "Advertencia", "error")
                 
            elif file_path:  # Si el usuario seleccionó una ruta
                mensaje = self.procesor.ExportarDataFrame_bcp(file_path)
                self.show_message(mensaje, "Exportación")
        except ValueError as e:
            self.show_message(str(e),"Problemas con la exportación","warning")

    def cargarTable(self):
        num_filas, monto_filas, num_filas_rev, monto_filas_rev, num_filas_atipicos = (
            self.procesor.analizar_dataframe_BCP()
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


    def limpiarTable(self):
        for row in range(5):
            self.table.setItem(row, 1, QTableWidgetItem("0"))
