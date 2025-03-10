
from PySide6.QtCore import QThread, Signal
from database.connection import SAPDataBaseManager
from database.querys import GET_INVOICES,GET_PAGO_EFECTUADO
import pandas as pd




class DatabaseWorker(QThread):
    result_ready=Signal(object)

    def __init__(self,db_type="SAP",params=None):
        super().__init__()
        self.db_type=db_type
        self.df=None
        self.params=params


    def run(self):
        db_manager=None

        if self.db_type=="SAP":
            db_manager=SAPDataBaseManager()
        if db_manager:
            self.df=db_manager.fetch_data_param(GET_PAGO_EFECTUADO,self.params)
            self.df = self.transform_data(self.df)
            self.result_ready.emit(self.df)


    def transform_data(self, df: pd.DataFrame):
        """Agrupa los bancos y cuentas en listas para cada cliente."""
        if df is None or df.empty:
            return df

        # Agrupar por CardCode y mantener listas de bancos y cuentas
        data = {
            "CardCode": ["P10459829321", "P20606059532"],
            "CardName": ["ROJAS ABRIGO CHRISTIAN MIGUEL", "PARYEX PERU E.I.R.L."],
            "LicTradNum":["10459829321","20606059532"],
            "Debit":[47.16,55.14],
            "LineMemo":["PAGO MASIVO INGRESO MARKET PLACE COOLBOX - ENERO I","PAGO MASIVO INGRESO MARKET PLACE COOLBOX - ENERO I"],
            "Ref1":["ENERO I","ENERO I"],
            # "Ref2":["10459829321","20606059532"],
            "BankName": ["BANCO BCP", "SCOTIABANK"],
            "DflAccount": ["193-99369645-0-76","00922420037758733278"],

        }
        df_data = pd.DataFrame(data)
        df=pd.concat([df,df_data])
        df.sort_values("CardCode",inplace=True)

        df = df.dropna(subset=["BankName", "DflAccount"])  # Eliminar filas con NaN en estas columnas
        # Excluir las columnas "BankName" y "DflAccount" del agrupamiento
        group_columns = df.columns.difference(["BankName", "DflAccount"]).tolist()
        df_grouped = df.groupby(group_columns, as_index=False).agg({
            "BankName": lambda x: list(x.unique()),  # Convertir en lista con valores únicos
            "DflAccount": lambda x: list(x.unique())  # Convertir en lista con valores únicos
        })

        # Convertir valores de BankName a listas si no lo son
        df_grouped["BankName"] = df_grouped["BankName"].apply(lambda x: x if isinstance(x, list) else [])
        df_grouped["DflAccount"] = df_grouped["DflAccount"].apply(lambda x: x if isinstance(x, list) else [])

        # Agregar columna de cuenta seleccionada (por defecto la primera)
        df_grouped["BankNameSeleccionado"] = df_grouped["BankName"].apply(lambda x: x[0] if x else None)
        df_grouped["DflAccountSeleccionado"] = df_grouped["DflAccount"].apply(lambda x: x[0] if x else None)

        # print("Transformación de datos completada:", df_grouped.head())  # Debug
        return df_grouped

