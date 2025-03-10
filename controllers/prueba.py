import pyodbc
import pandas as pd
# Reemplaza 'DSN_SAP' con el DSN configurado en ODBC
conn = pyodbc.connect("DSN=HANA;UID=HANA;PWD=@PassRash2024")


# cursor = conn.cursor()
# cursor.execute("SELECT TOP 100 * FROM SBO_RASH_PRODUCCION.OINV")

query ="SELECT TOP 100 * FROM SBO_RASH_PRODUCCION.OINV"

df = pd.read_sql(query,conn)

df.head()





