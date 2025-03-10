

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QTableView, QStyledItemDelegate, QCheckBox, QWidget, QHBoxLayout, QComboBox


import pandas as pd

class ComboBoxDelegate(QStyledItemDelegate):
    """Delegate para mostrar un QComboBox en la columna 'BankNameSeleccionado'."""
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        return editor
    def setEditorData(self, editor, index):
        """Configura el QComboBox con las opciones disponibles en la columna 'BankName'."""
        model = index.model()
        row = model.visible_rows[index.row()]  # Ajustar índice correctamente ✅

        bancos = model._df.at[row, "BankName"]
        
        # Convertir a lista si es necesario
        if not isinstance(bancos, list):
            bancos = [bancos] if pd.notna(bancos) else []

        editor.clear()

        # Si hay más de un banco, agregar "Revisar" como opción por defecto
        if len(bancos) > 1:
            editor.addItem("Revisar")

        # Agregar las opciones reales de bancos
        for banco in bancos:
            editor.addItem(banco)

        # Seleccionar el valor actual
        current_value = model._df.at[row, "BankNameSeleccionado"]
        if not current_value and len(bancos) > 1:
            current_value = "Revisar"  # Si no hay valor, asignamos "Revisar"

        index = editor.findText(current_value)
        if index >= 0:
            editor.setCurrentIndex(index)


    def setModelData(self, editor, model, index):
        """Guarda el valor seleccionado en la columna 'BankNameSeleccionado' y actualiza la cuenta asociada."""
        row = model.visible_rows[index.row()]  # 🔄 Ajuste correcto del índice

        selected_bank = editor.currentText()

        bancos = model._df.at[row, "BankName"]
        cuentas = model._df.at[row, "DflAccount"]

        # Convertir a lista si es necesario
        if not isinstance(bancos, list):
            bancos = [bancos] if pd.notna(bancos) else []

        if not isinstance(cuentas, list):
            cuentas = [cuentas] if pd.notna(cuentas) else []

        if selected_bank == "Revisar":
            model._df.at[row, "BankNameSeleccionado"] = "Revisar"
            model._df.at[row, "DflAccountSeleccionado"] = "Revisar"
        elif selected_bank in bancos:
            idx = bancos.index(selected_bank)
            model._df.at[row, "BankNameSeleccionado"] = selected_bank
            model._df.at[row, "DflAccountSeleccionado"] = cuentas[idx] if idx < len(cuentas) else "Desconocido"

        model.dataChanged.emit(index, index)


class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df_original = df.copy()  # Guardar una copia original
        self._df = df.copy()  # Este se modificará
        self.visible_columns = ["CardCode", "CardName", "Debit","Bancos", "BankNameSeleccionado", "DflAccountSeleccionado"]
        self.visible_rows = df.index.tolist()

        self._df["Bancos"] = self._df["BankName"].apply(lambda x: len(x) if isinstance(x, list) else (1 if pd.notna(x) else 0))

        for row in range(len(self._df)):
            bancos = self._df.at[row, "BankName"]

            # Convertir a lista si es necesario
            if not isinstance(bancos, list):
                bancos = [bancos] if pd.notna(bancos) else []

            # if len(bancos) > 1:
            #     self._df.at[row, "BankNameSeleccionado"] = "Revisar"
            #     self._df.at[row, "DflAccountSeleccionado"] = "Revisar"


    def rowCount(self, parent=None):
        return len(self.visible_rows)  # Solo cuenta las filas visibles

    def columnCount(self, parent=None):
        return len(self.visible_columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = self.visible_rows[index.row()]  # Obtener la fila correcta
        column_name = self.visible_columns[index.column()]
        value = self._df[column_name].iloc[row]

        if role == Qt.ItemDataRole.DisplayRole:
            if column_name == "BankNameSeleccionado":
                return value  # Mostrar solo el banco seleccionado
            if isinstance(value, list):  
                return ", ".join(value)  # Convertir listas a string separado por comas
            return str(value) if pd.notna(value) else ""

        return None
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Usar visible_columns en lugar de self._df.columns
                if section < len(self.visible_columns):
                    return self.visible_columns[section]
                return None  # Evitar index error si la sección es inválida
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None


    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        row = self.visible_rows[index.row()]  # Ajustar índice
        column_name = self.visible_columns[index.column()]

        if role == Qt.ItemDataRole.EditRole and column_name == "BankNameSeleccionado":
            self._df.at[row, "BankNameSeleccionado"] = value

            # Buscar la cuenta asociada al banco seleccionado y actualizarla
            bancos = self._df.at[row, "BankName"]
            cuentas = self._df.at[row, "DflAccount"]

            if isinstance(bancos, list) and isinstance(cuentas, list):  # Asegurar que son listas
                if value in bancos:
                    idx = bancos.index(value)
                    self._df.at[row, "DflAccountSeleccionado"] = cuentas[idx]

            self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
            return True

        return False


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        if index.column() >= len(self.visible_columns):
            return Qt.ItemFlag.NoItemFlags  # Evitar acceder a índices fuera de rango

        flags = super().flags(index)

        if self.visible_columns[index.column()] == "BankNameSeleccionado":
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

        return flags


    def setVisibleColumns(self, columns):
        if columns:
            self.visible_columns = columns
        else:
            self.visible_columns = ["CardCode", "CardName", "Debit","Bancos", "BankNameSeleccionado", "DflAccountSeleccionado"]
        self.layoutChanged.emit()

    def setVisibleRows(self, only_revisar=True):
        """Muestra solo las filas que contienen 'Revisar' en BankNameSeleccionado o DflAccountSeleccionado."""
        if only_revisar:
            self.visible_rows = self._df[self._df["Bancos"] > 1].index.tolist()
            # self.visible_rows = self._df[
            #     (self._df["BankNameSeleccionado"].astype(str).str.contains("Revisar", na=False)) |
            #     (self._df["DflAccountSeleccionado"].astype(str).str.contains("Revisar", na=False))
            # ].index.tolist()
        else:
            self.visible_rows = self._df.index.tolist()  # Mostrar todas las filas

        self.layoutChanged.emit()  # Actualizar la tabla y el modelo
        self.updateComboBoxDelegate()  # 🔄 Volver a asignar el delegado ✅


    def updateComboBoxDelegate(self):
        """Reasigna el ComboBoxDelegate después de un filtrado."""
        if hasattr(self, "table") and self.table is not None:  # Evitar errores si table no está inicializada
            delegate = ComboBoxDelegate(self.table)
            for col_name in ["BankNameSeleccionado"]:
                if col_name in self.visible_columns:
                    col_index = self.visible_columns.index(col_name)
                    self.table.setItemDelegateForColumn(col_index, delegate)
    def ObtenerData(self):
        return self._df
