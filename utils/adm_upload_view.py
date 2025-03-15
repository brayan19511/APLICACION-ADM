
from  PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QHBoxLayout,QPushButton,QLabel,QLineEdit,QFileDialog
# ,QMessageBox,QSizePolicy
# import time
# import threading



class UploadFile(QWidget):

    def __init__(self,layouWidget,progress_widget=None):
        super().__init__()
        self.file_path = None
        self.uploadWidget(layouWidget)
        self.progress_widget = progress_widget


    def uploadWidget(self,layouWidget:QHBoxLayout):
        
        upload_widget=QWidget()
        layout_upload=QHBoxLayout(upload_widget)

        texto =QLabel("Seleccionar documento ")
        self.inputFile=QLineEdit()
        btnExaminar=QPushButton("Examinar")

        btnExaminar.clicked.connect(self.openFileDialog)
        self.inputFile.setReadOnly(True)

        layout_upload.addWidget(texto)
        layout_upload.addWidget(self.inputFile)
        layout_upload.addWidget(btnExaminar)
        
        layouWidget.addWidget(upload_widget)
        layouWidget.setAlignment(upload_widget,Qt.AlignmentFlag.AlignTop) 

    def openFileDialog(self):
        file,_=QFileDialog.getOpenFileName(self,"Abrir archivo Excel","","Archivos Excel (*.xls *.xlsx *.xlsm)")
        if file:
            self.file_path = file 
            self.inputFile.setText(file)
            # threading.Thread(target=self.simular_progreso, daemon=True).start()
        else:
            self.file_path = None
            self.inputFile.setText("")

    def getFile(self):
        return self.file_path


