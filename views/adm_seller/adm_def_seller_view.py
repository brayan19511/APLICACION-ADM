
# from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QLineEdit,QMessageBox,QTableWidget,QTableWidgetItem,QHeaderView,QTableView
from  PySide6.QtCore import Qt
from utils.get_plantilla_bcp_seller import PlantillaBCP

from controllers.adm_seller_controller import DatabaseWorker
from models.pandas_model import PandasModel,ComboBoxDelegate

import pandas as pd
class AdmSellerContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout_Main=QVBoxLayout()  
        self.visibleCol=True
        self.hide_revisar = True 
        self.headerWidget()
        self.buttonSelletWidget()
        self.sellerWidget()

        self.setLayout(self.layout_Main)

    def headerWidget(self):
        headerWidget=QWidget()
        headerLayout=QHBoxLayout(headerWidget)

        texto=QLabel("N° Pago Efectuado")
        pagoEfectuado=QLineEdit()
        pagoEfectuado.setText("62705399")
        
        button=QPushButton("Cargar Pago Efectuado")
        button.clicked.connect(lambda : self.fech_data(pagoEfectuado.text()))

        headerLayout.addWidget(texto)
        headerLayout.addWidget(pagoEfectuado)
        headerLayout.addWidget(button)
        self.layout_Main.addWidget(headerWidget)
        self.layout_Main.setAlignment(headerWidget,Qt.AlignmentFlag.AlignTop) 


    def sellerWidget(self):

        sellerWidget=QWidget()
        sellerLayout=QVBoxLayout(sellerWidget)
        # 62705399
        self.label_totals = QLabel("Filas: 0 | Total: 0")
        self.table=QTableView()
        # button_export = QPushButton("Exportar a Excel")
        # button_export.clicked.connect(lambda: self.exportData("datos_exportados.xlsx"))

        sellerLayout.addWidget(self.label_totals)
        # sellerLayout.addWidget(button_export)
        sellerLayout.addWidget(self.table)
        self.layout_Main.addWidget(sellerWidget,1)
        # self.layout_Main.setAlignment(sellerWidget,Qt.AlignmentFlag.AlignTop) 


    def buttonSelletWidget(self):
        buttonWidget=QWidget()
        buttonLayout=QHBoxLayout(buttonWidget)
        buttonCol=QPushButton("columnas visibles")
        buttonCol.clicked.connect(self.columnsVisible)
        buttonFilter=QPushButton("Filtrar 'Revisar'")
        buttonFilter.clicked.connect(self.toggleRowsVisibility)
        buttonBCP=QPushButton("Generar Plantilla")
        buttonBCP.clicked.connect(self.getPlantilla)

        buttonLayout.addWidget(buttonCol)
        buttonLayout.addWidget(buttonFilter)
        buttonLayout.addWidget(buttonBCP)
        self.layout_Main.addWidget(buttonWidget)
        self.layout_Main.setAlignment(buttonWidget,Qt.AlignmentFlag.AlignTop) 



    def fech_data(self,pago_efectuado):
        print("procesando consulta sap")
        selected_db='SAP'
        self.worker=DatabaseWorker(selected_db,pago_efectuado)
        self.worker.result_ready.connect(self.display_data)
        self.worker.start()

    def display_data(self, data):
        if data is not None:
            self.df = data
            self.model = PandasModel(self.df)
            self.table.setModel(self.model)
            # Obtener totales y actualizar el label
            total_filas, total_monto = self.getTotalInfo()
            self.label_totals.setText(f"Filas: {total_filas} | Total: S/ {total_monto:,.2f}")

            # Asegurar que la columna "BankNameSeleccionado" está en visible_columns
            if "BankNameSeleccionado" not in self.model.visible_columns:
                self.model.visible_columns.append("BankNameSeleccionado")
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            delegate = ComboBoxDelegate(self.table)

            # Obtener índice de la columna en visible_columns antes de asignar el delegado
            if "BankNameSeleccionado" in self.model.visible_columns:
                col_index = self.model.visible_columns.index("BankNameSeleccionado")
                self.table.setItemDelegateForColumn(col_index, delegate)

            print("Delegate asignado a columna BankNameSeleccionado")  # Debug
        

    def columnsVisible(self):
        columns = None
        if self.visibleCol:
            columns = ["CardCode", "CardName", "Debit","LineMemo", "BankNameSeleccionado", "DflAccountSeleccionado"]
            self.visibleCol = False
        else:
            self.visibleCol = True

        self.model.setVisibleColumns(columns)

        # 🔄 Reasignar el ComboBoxDelegate después de actualizar las columnas visibles
        if "BankNameSeleccionado" in self.model.visible_columns:
            col_index = self.model.visible_columns.index("BankNameSeleccionado")
            self.table.setItemDelegateForColumn(col_index, ComboBoxDelegate(self.table))
    def toggleRowsVisibility(self):
        self.model.setVisibleRows(self.hide_revisar)  # Aplicar filtro
        self.hide_revisar = not self.hide_revisar  # Alternar estado
    def exportData(self, file_path="export.xlsx"):
        if hasattr(self, "df"):
            try:
                # Exportar a Excel
                self.df.to_excel(file_path, index=False)
                print(f"✅ Archivo exportado correctamente a {file_path}")
            except Exception as e:
                print(f"❌ Error al exportar: {e}")
        else:
            print("⚠ No hay datos cargados para exportar.")
    def getTotalInfo(self):
        if hasattr(self, "df"):
            total_filas = len(self.df)
            total_monto = self.df["Debit"].sum()
            print(f"📊 Total Filas: {total_filas}, Monto Total: S/ {total_monto:,.2f}")
            return total_filas, total_monto
        else:
            print("⚠ No hay datos disponibles.")
            return 0, 0
        
    def getPlantilla(self):
        plantilla=PlantillaBCP(self.model.ObtenerData())
        df_bcp=plantilla.proces_data_seller()
        df_bcp.to_excel("plantillaBCP.xlsx")



