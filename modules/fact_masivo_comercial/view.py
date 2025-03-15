from  PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.view import BaseView
from utils.adm_upload_view import UploadFile

class FacturaMasivoComercialView(BaseView):
    def __init__(self):
        super().__init__()
        self.layoutMain=QVBoxLayout()

        titulo=QLabel("Gestión Facturas Masivo Comercial ")
        self.layoutMain.addWidget(titulo)
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # Centrar texto
        self.upload_file_widget = UploadFile(self.layoutMain)

        self.headerWidget()
        self.botones()
        self.tableDetalle()

        self.setLayout(self.layoutMain)

    def headerWidget(self):
        
        headerWidget=QWidget()
        headerLayout=QHBoxLayout(headerWidget)
        folio=QLabel("Ultimo Folio: ")
        folioTxt=QLineEdit()
        tc=QLabel("T.C :")
        tcTxt=QLineEdit()
        
        btnCargar=QPushButton("Cargar Archivo")

        headerLayout.addWidget(folio)
        headerLayout.addWidget(folioTxt)
        headerLayout.addWidget(tc)
        headerLayout.addWidget(tcTxt)
        headerLayout.addWidget(btnCargar)
        headerLayout.setAlignment(Qt.AlignmentFlag.AlignTop) 
        self.layoutMain.addWidget(headerWidget)
    def botones(self):
        botonWidget=QWidget()
        botonLayout=QHBoxLayout(botonWidget)
        botonExcel=QPushButton("Generar Excel")
        botonTXT=QPushButton("Generar TXT")

        botonLayout.addWidget(botonExcel)
        botonLayout.addWidget(botonTXT )
        self.layoutMain.addWidget(botonWidget)
        

    def tableDetalle(self):
        self.table=QTableWidget()
        labels = [
            "Cantidad de documentos",
            "Cantidad de documentos Soles",
            "Cantidad de documentos Dolares",
            "Monto Total",
            "Monto Total Soles",
            "Monto Total Dolares",
            "Cantidad de filas a revisar",
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

        self.layoutMain.addWidget(self.table,1)


