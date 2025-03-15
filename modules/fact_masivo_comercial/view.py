from datetime import datetime
from  PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,QLabel,QLineEdit,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QFileDialog,QComboBox
from PySide6.QtCore import Qt
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QFont

from utils.adm_upload_view import UploadFile
from core.view import BaseView
from modules.fact_masivo_comercial.model import ProcesarComercial

import pandas as pd

class FacturaMasivoComercialView(BaseView):
    def __init__(self):
        super().__init__()
        self.layoutMain=QVBoxLayout()
        self.procesor=ProcesarComercial()
        titulo=QLabel("Gestión Facturas Masivo Comercial ")
        self.layoutMain.addWidget(titulo)
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # Centrar texto
        self.upload_file_widget = UploadFile(self.layoutMain)
        self.upload_file_widget.file_selected.connect(self.updateComboBox)

        self.headerWidget()
        self.botones()
        self.tableDetalle()
        self.textLog()

        self.setLayout(self.layoutMain)

    def headerWidget(self):
        
        headerWidget=QWidget()
        headerLayout=QHBoxLayout(headerWidget)
        sheetCombo=QLabel("Seleccione la hoja: ")
        self.combo_sheet = QComboBox()
        folio=QLabel("Ultimo Folio: ")
        self.folioTxt=QLineEdit()
        tc=QLabel("T.C :")
        self.tcTxt=QLineEdit()
        
        self.combo_sheet.setFixedWidth(200)

        btnCargar=QPushButton("Cargar Archivo")
        btnCargar.clicked.connect(self.CargarArchivo)
        headerLayout.addWidget(sheetCombo)
        headerLayout.addWidget(self.combo_sheet)
        headerLayout.addWidget(folio)
        headerLayout.addWidget(self.folioTxt)
        headerLayout.addWidget(tc)
        headerLayout.addWidget(self.tcTxt)
        headerLayout.addWidget(btnCargar)
        headerLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 
        self.layoutMain.addWidget(headerWidget)
    def botones(self):
        botonWidget=QWidget()
        botonLayout=QHBoxLayout(botonWidget)
        botonExcel=QPushButton("Generar Excel")
        botonExcel.clicked.connect(self.ExportarArchivo)
        botonTXT=QPushButton("Generar TXT")
        botonTXT.clicked.connect(self.ExportarArchivoTXT)

        botonLayout.addWidget(botonExcel)
        botonLayout.addWidget(botonTXT )

        self.layoutMain.addWidget(botonWidget)
        

    def tableDetalle(self):
        tableWidget=QWidget()
        tableLayout=QHBoxLayout(tableWidget)
        self.table=QTableWidget()
        labels = [
            "Cantidad de filas a revisar",
            "Cantidad de documentos",
            "Cantidad de documentos Soles",
            "Cantidad de documentos Dolares",
            "Monto Total",
            "Monto Total Soles",
            "Monto Total Dolares"
        ]   
        self.table.setColumnCount(2)
        self.table.setRowCount(len(labels))
        self.table.setHorizontalHeaderLabels(["Descripción","Valor"])
        self.table.verticalHeader().setVisible(False)
        for row,label in enumerate(labels):
            self.table.setItem(row,0,QTableWidgetItem(label))
            self.table.setItem(row,1,QTableWidgetItem("0"))

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        
        tableLayout.addWidget(self.table,1)
        tableLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layoutMain.addWidget(tableWidget,1)
    def textLog(self):
        logWidget=QWidget()
        logLayout=QHBoxLayout(logWidget)
        self.statusLog=QTextEdit()
        self.statusLog.setReadOnly(True)
        self.statusLog.setMaximumHeight(100) 
        logLayout.addWidget(self.statusLog)
        logLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layoutMain.addWidget(logWidget)
    def log_status(self,message):
        self.statusLog.append(message)
        QCoreApplication.processEvents()

    def CargarArchivo(self):
        folio = self.folioTxt.text().strip()
        tc = self.tcTxt.text().strip()
        try:
            folio = int(folio)
        except ValueError:
            self.show_message("Por favor escoger un folio correcto")
            return  # Detener la ejecución si hay error

        # Validar si el tipo de cambio es un número flotante
        try:
            tc = float(tc)
        except ValueError:
            self.show_message("Por favor escoger un tc correcto")
            return  # Detener la ejecución si hay error


        try:
            filepath=self.upload_file_widget.getFile()
            hoja_seleccionada = self.combo_sheet.currentText()
            
            self.procesor.CargarDataFrame(filepath,hoja_seleccionada,folio,tc)
            self.procesor.validate_columns()
            self.procesor.ProcesarData()
            self.procesor.CargaPlantilla()
            self.cargarTable()
        except ValueError as e:
            self.limpiarTable()
            self.show_message(str(e),"Problemas con el archivo","warning")
        except FileNotFoundError as e:  # ✅ Manejo de archivos inexistentes
            self.limpiarTable()
            self.show_message(str(e), "Archivo no encontrado", "error")

    def ExportarArchivo(self):
        """Abre QFileDialog y llama al modelo para exportar"""
        fecha_actual = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", f"FAC_MASIVO_{fecha_actual}.xlsx", "Excel Files (*.xlsx)")
        try:
            if(self.upload_file_widget.getFile()!= self.procesor.getFilePath()):
                self.show_message( "Porfavor Cargue el archivo antes de exportar","Advertencia", "error")
           
            elif file_path:  # Si el usuario seleccionó una ruta
                mensaje = self.procesor.exportData(file_path)
                self.show_message(mensaje, "Exportación")
        except ValueError as e:
            self.show_message(str(e),"Problemas con la exportación","warning")
    def ExportarArchivoTXT(self):
        """Abre QFileDialog y llama al modelo para exportar"""
        fecha_actual = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", f"FAC_MASIVO_{fecha_actual}.xlsx", "Excel Files (*.xlsx)")
        try:
            if(self.upload_file_widget.getFile()!= self.procesor.getFilePath()):
                self.show_message( "Porfavor Cargue el archivo antes de exportar","Advertencia", "error")
           
            elif file_path:  # Si el usuario seleccionó una ruta
                mensaje = self.procesor.exportTxt(file_path)
                self.show_message(mensaje, "Exportación")
        except ValueError as e:
            self.show_message(str(e),"Problemas con la exportación","warning")


# complementarios
    def updateComboBox(self,filepath):
        """Cargar las hojas del archivo combo box"""
        try:
            sheets=pd.ExcelFile(filepath).sheet_names
            self.combo_sheet.clear()
            self.combo_sheet.addItems(sheets)
        except Exception as e:
            self.show_message("No se pudo leer el archivo","Warning","warning")

    def limpiarTable(self):
        for row in range(7):
            self.table.setItem(row, 1, QTableWidgetItem("0"))
    def cargarTable(self):
        filasrev,doc,docsol,docdol,monto,montosol,montodol = (
            self.procesor.analizarData()
        )
        valores = [
            f"{filasrev}",
            f"{doc}",
            f"{docsol}",
            f"{docdol}",
            f"{monto:,.2f}",
            f"S/  {montosol:,.2f}",
            f"US$ {montodol:,.2f}",
        ]
        for row, value in enumerate(valores):
            self.table.setItem(row, 1, QTableWidgetItem(f"{value}"))

