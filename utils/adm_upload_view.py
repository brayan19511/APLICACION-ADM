
from  PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QWidget,QHBoxLayout,QPushButton,QLabel,QLineEdit,QFileDialog
# ,QMessageBox,QSizePolicy
# import time
# import threading



class UploadFile(QWidget):
    file_selected = Signal(str)

    def __init__(self, layouWidget):
        super().__init__()
        self.file_path = None
        self.uploadWidget(layouWidget)


    def uploadWidget(self, layouWidget: QHBoxLayout):
        
        upload_widget=QWidget()
        layout_upload=QHBoxLayout(upload_widget)

        texto =QLabel("Seleccionar documento ")
        self.inputFile=QLineEdit()
        self.browse_button=QPushButton("Examinar")

        self.browse_button.clicked.connect(self.openFileDialog)
        self.inputFile.setReadOnly(True)

        layout_upload.addWidget(texto)
        layout_upload.addWidget(self.inputFile)
        layout_upload.addWidget(self.browse_button)
        
        layouWidget.addWidget(upload_widget)
        layouWidget.setAlignment(upload_widget,Qt.AlignmentFlag.AlignTop) 

    def openFileDialog(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo Excel",
            "",
            "Archivos Excel (*.xls *.xlsx *.xlsm)",
        )
        if file:
            self.file_path = file 
            self.inputFile.setText(file)
            self.file_selected.emit(file)
            # threading.Thread(target=self.simular_progreso, daemon=True).start()
        else:
            # Cancelar el diálogo no debe olvidar un archivo ya seleccionado.
            return

    def getFile(self):
        return self.file_path

    def set_enabled(self, enabled):
        self.browse_button.setEnabled(enabled)


