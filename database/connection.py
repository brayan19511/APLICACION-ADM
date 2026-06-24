import pyodbc
import pandas as pd
from config import DATABASE_DSN,DATABASE_PASS,DATABASE_USER

class DataBaseManager:
    def connect(self):
        raise NotImplementedError("Metodo 'connect' debe ser implementado en la subclase")
    def fetch_data(self, query, params=None):
        """Ejecuta una consultar SQL y devuelve un DataFrame de Pandas"""
        with self.connect() as connection:
            return pd.read_sql(query, connection, params=params)
    
class SAPDataBaseManager(DataBaseManager):
    """Conexion a la base de datos de SAP por ODBC"""
    def __init__(self):
        if not all((DATABASE_DSN, DATABASE_USER, DATABASE_PASS)):
            raise RuntimeError(
                "Falta configurar DATABASE_DSN, DATABASE_USER o DATABASE_PASS."
            )

    def connect(self):
        return pyodbc.connect(
            f"DSN={DATABASE_DSN};UID={DATABASE_USER};PWD={DATABASE_PASS}"
        )
        
    def fetch_data_param(self,query,params=None):
        """ejecutar una consulta SAP con parametros"""
        try:
            return self.fetch_data(query, params=params)
        except Exception as exc:
            raise RuntimeError(f"Error al consultar SAP por ODBC: {exc}") from exc
        
    
