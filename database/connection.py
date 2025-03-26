import pyodbc
import pandas as pd
from config import DATABASE_DSN,DATABASE_PASS,DATABASE_USER

class DataBaseManager:
    def connect(self):
        raise NotImplementedError("Metodo 'connect' debe ser implementado en la subclase")
    def fech_data(self,query):
        """Ejecuta una consultar SQL y devuelve un DataFrame de Pandas"""
        conn =self.connect()

        if conn:
            df=pd.read_sql(query,conn)
            conn.close()
            return df
        return None
    
class SAPDataBaseManager(DataBaseManager):
    """Conexion a la base de datos de SAP por ODBC"""
    def __init__(self):
        self.conn=pyodbc.connect(f"DSN={DATABASE_DSN};UID={DATABASE_USER};PWD={DATABASE_PASS}")
        
    def fetch_data_param(self,query,params=None):
        """ejecutar una consulta SAP con parametros"""
        try:
            if params:
                df=pd.read_sql(query,self.conn,params=params)
            else:
                print("consulta sin partams")
                df=pd.read_sql(query,self.conn)
            return df

        except Exception as e:
            print(f"Error en ODBC: {e}")
            return None
        
    
