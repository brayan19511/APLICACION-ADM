import os
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter

import pandas as pd
import numpy as np


class NcrDefProcesor:

    def __init__(self,path=None):
        self.path=path
        self.df=None

    def getFilePath(self):
        return self.path
    def getDf(self):
        return self.df
    def CargarDataFrame(self,file_path):
        if file_path=="" or file_path is None:
            raise ValueError(f"No se ha seleccionado un arhivo.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo '{file_path}' no existe.")
        try:
            self.path=file_path
            self.df= pd.read_excel(
                                file_path, 
                                dtype={
                                        'Cuenta Seleccionada': str,"Clasificacion Banco":str
                                        ,'N° DOCUMENTO':str,'DNI/RUC':str
                                        ,'N° CUENTA':str,'CCI':str
                                       }
                                   )
        except Exception as e:
            raise ValueError(f"❌ Error al exportar el archivo: {str(e)}")
        
    def validate_columns_DEF(self):
        REQUIREMENT_COLUMNS=['N° NOTA CRÉDITO',
                        'FECHA NCR',
                        'TIPO DOC.',
                        'N° DOCUMENTO',
                        'DNI/RUC',
                        'NOMBRE CLIENTE/RAZÓN SOCIAL',
                        'IMPORTE',
                        'FECHA REGISTRO DATOS',
                        'CUENTA TITULAR',
                        'N° CUENTA',
                        'CCI',
                        'BANCO',
                        'ESTADO',
                        'CORREO '
                        ]
        
        missing_columns = [col for col in REQUIREMENT_COLUMNS if col not in self.df.columns]
        
        if missing_columns:
            self.df=None
            raise ValueError(f"❌ Faltan las siguientes columnas: {', '.join(missing_columns)}")

        
    def procesarDEF(self):
        self.df=self.df[self.df["ESTADO"]=="Datos Bancarios"].copy()
        self.clasificacion()
        self.ajustarColumnas()

    def clasificacion(self):
        #aseguramos que no tenga espaciones 
        self.df["DNI/RUC"] = self.df["DNI/RUC"].str.strip()
        self.df["N° DOCUMENTO"] = self.df["N° DOCUMENTO"].str.strip()

        # agregamos columna formateada
        self.df["DEF FORMATEADO"]=self.df["N° NOTA CRÉDITO"].str.replace("-",'',regex=False)
        # modificamos el ruc 10 quitando 2 primeros y ultimo digito
        self.df["DNI/RUC"]=self.df["DNI/RUC"].apply(lambda x:x[2:-1] if len(x)==11 and x.startswith("10") else x)
        # agregando o quitando digitos a los CEX
        self.df["DNI/RUC"]=self.df.apply(lambda row: self.ajusteCEX(row['DNI/RUC'],row["TIPO DOC."]),axis=1)
        self.df["N° DOCUMENTO"]=self.df.apply(lambda row: self.ajusteCEX(row['N° DOCUMENTO'],row["TIPO DOC."]),axis=1)
        # Verificamos si es igual N° documento y DNI/RUC
        self.df["Doc. Verificar"]=np.where(self.df["DNI/RUC"]==self.df["N° DOCUMENTO"],"ok","revisar")
        self.df["Clasificacion Doc"]=self.df["DNI/RUC"].apply(self.clasificacionDoc)

        # Reemplazando banco central de reserva por el BCP
        self.df["BANCO"]=self.df["BANCO"].replace("BANCO CENTRAL RESERVA DEL PERU",'BANCO DE CREDITO DEL PERU')
        self.df["Clasificacion Banco"]=self.df.apply(lambda row: self.clasificacionBanco(row["BANCO"],row["N° CUENTA"],row["CCI"]),axis=1)
        self.df["Cuenta Seleccionada"]=np.where(self.df["BANCO"]=="BANCO DE CREDITO DEL PERU",self.df["N° CUENTA"],self.df["CCI"])
        # ajuste de columnas
        
        
    # funciones para realizar modificaciones 
    def clasificacionDoc(self,x):
        if len(x)==8:
            return "1"
        elif len(x)==9:
            return "3"
        elif len(x)==11:
            return "6"
        else:
            return "4"

    def clasificacionBanco(self,banco,cuenta,cci):
        cuenta=str(cuenta)
        cci=str(cci)
        if str(banco)=='BANCO DE CREDITO DEL PERU':
            if len(cuenta)==13:
                return "C"
            elif len(cuenta)==14:
                return "A"
            else:
                return f"revisar BCP: {len(cuenta)} digitos"
        else:
            if len(cci)==20:
                return "B"
            else:
                f"revisar CIC: {len(cci)} digitos"
    
    def ajusteCEX(self,doc,tipoDoc):
        if str(tipoDoc).startswith("3"):
            if(len(doc)<9):
                return doc.zfill(9)
            elif(len(doc)>9):
                return doc[-9:]
        return doc
    

    def ajustarColumnas(self):
        self.df.insert(3,'DEF FORMATEADO',self.df.pop('DEF FORMATEADO'))
        self.df.insert(10,'Doc. Verificar',self.df.pop('Doc. Verificar'))
        self.df.insert(11,'Clasificacion Doc',self.df.pop('Clasificacion Doc'))
        self.df.insert(21,'Clasificacion Banco',self.df.pop('Clasificacion Banco'))
        self.df.insert(22,'Cuenta Seleccionada',self.df.pop('Cuenta Seleccionada'))
    
    


    def analizar_dataframe_def(self):
        num_filas,monto_filas,num_filas_rev,monto_filas_rev,num_filas_atipicos=0,0,0,0,0
        num_filas=self.df.shape[0]
        monto_filas=self.df["IMPORTE"].sum()
        num_filas_rev=self.df[
            self.df["Doc. Verificar"].str.contains("revisar",na=False) |
            self.df["Clasificacion Banco"].str.contains("revisar",na=False)
        ].shape[0]
        monto_filas_rev=self.df[
            self.df["Doc. Verificar"].str.contains("revisar",na=False) |
            self.df["Clasificacion Banco"].str.contains("revisar",na=False)
        ]["IMPORTE"].sum()

        num_filas_atipicos=self.df[self.df["IMPORTE"]>1500].shape[0]


        return num_filas,monto_filas,num_filas_rev,monto_filas_rev,num_filas_atipicos




    def ExportarDataFrame_def(self,file_path="export.xlsx"):
        
        if self.df is None:
            raise ValueError("Aun no se ha cargado el archivo")

        try:

            self.df.to_excel(file_path, index=False)
            # Aplicar colores con openpyxl
            wb = load_workbook(file_path)
            hoja = wb.active  
            fill_blue = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
            # Obtener índices de las columnas relevantes
            col_estado = self.df.columns.get_loc("Doc. Verificar") + 1  # +1 porque openpyxl usa índices desde 1
            col_clasificacion = self.df.columns.get_loc("Clasificacion Banco") + 1
            # Pintar los encabezados
            hoja.cell(row=1, column=col_estado).fill = fill_blue
            hoja.cell(row=1, column=col_clasificacion).fill = fill_blue
            # Autoajustar el ancho de las columnas
            for col_num, column_cells in enumerate(hoja.iter_cols(min_row=1, max_row=1), start=1):
                max_length = 0
                col_letter = get_column_letter(col_num)  

                for cell in column_cells:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))

                adjusted_width = max_length + 2  
                hoja.column_dimensions[col_letter].width = adjusted_width
            # Guardar cambios
            wb.save(file_path)
            wb.close()
            return f"✅ Archivo guardado en: {file_path}"

        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            return e

    
    
    

class NcrBCPProcesor:
    def __init__(self,path=None):
        self.path=path
        self.df=None
        self.df_bcp=None
    def getFilePath(self):
        return self.path
    def getDf(self):
        return self.df_bcp
    def CargarDataFrame(self,file_path):
        if file_path=="" or file_path is None:
            raise ValueError(f"No se ha seleccionado un arhivo.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo '{file_path}' no existe.")
        try:
            self.path=file_path
            self.df= pd.read_excel(
                                file_path, 
                                dtype={
                                        'Cuenta Seleccionada': str,"Clasificacion Banco":str
                                        ,'N° DOCUMENTO':str,'DNI/RUC':str
                                        ,'N° CUENTA':str,'CCI':str
                                       }
                                   )
        except Exception as e:
            raise ValueError(f"❌ Error al exportar el archivo: {str(e)}")
    def validate_columns_BCP(self):
        REQUIREMENT_COLUMNS=['Clasificacion Banco',
                        'Cuenta Seleccionada',
                        'Clasificacion Doc',
                        'DNI/RUC',
                        'NOMBRE CLIENTE/RAZÓN SOCIAL',
                        'IMPORTE',
                        'DEF FORMATEADO',
                        ]
        
        missing_columns = [col for col in REQUIREMENT_COLUMNS if col not in self.df.columns]
        
        if missing_columns:
            self.df=None
            raise ValueError(f"❌ Faltan las siguientes columnas: {', '.join(missing_columns)}")
             
    def procesarBCP(self):
        self.df=self.df[self.df["ESTADO"]=="Datos Bancarios"].copy()
        self.Plantilla()

    def Plantilla(self)->pd.DataFrame:
        # df_plantilla=pd.read_excel('plantilla_lista.xlsx', dtype={'Cuenta Seleccionada': str,'DNI/RUC':str})
        plantillaBcp=[]
        for index,row in self.df.iterrows():

            fila1={
                "Tipo de Registro":"A",
                "Tipo de Cuenta de Abono":row["Clasificacion Banco"],
                "Cuenta de Abono":row["Cuenta Seleccionada"],
                "Tipo de Documento de Identidad":row["Clasificacion Doc"],
                "Número de Documento de Identidad":row["DNI/RUC"],
                "Correlativo de Documento de Identidad":"",
                "Nombre del proveedor":row["NOMBRE CLIENTE/RAZÓN SOCIAL"],
                "Tipo de Moneda de Abono":"S",
                "Monto del Abono":row["IMPORTE"],
                "Validación IDC del proveedor vs Cuenta":"S",
                "Cantidad Documentos relacionados al Abono":"0001",

                "Tipo de Documento a pagar":"",
                "Nro. del Documento":"",
                "Moneda Documento":"",
                "Monto del Documento":"",

            }
            fila2={
                "Tipo de Registro":"D",
                "Tipo de Cuenta de Abono":"",
                "Cuenta de Abono":"",
                "Tipo de Documento de Identidad":"",
                "Número de Documento de Identidad":"",
                "Correlativo de Documento de Identidad":"",
                "Nombre del proveedor":"",
                "Tipo de Moneda de Abono":"",
                "Monto del Abono":"",
                "Validación IDC del proveedor vs Cuenta":"",
                "Cantidad Documentos relacionados al Abono":"",

                "Tipo de Documento a pagar":"C",
                "Nro. del Documento":row["DEF FORMATEADO"],
                "Moneda Documento":"S",
                "Monto del Documento":row["IMPORTE"]

            }

            plantillaBcp.append(fila1)
            plantillaBcp.append(fila2)


        self.df_bcp=pd.DataFrame(plantillaBcp)
        # return df_plantillaBcp
    def analizar_dataframe_BCP(self):


        num_filas,monto_filas,num_filas_rev,monto_filas_rev,num_filas_atipicos=0,0,0,0,0
        num_filas=self.df.shape[0]
        monto_filas=self.df["IMPORTE"].sum()
        num_filas_rev=self.df[
            self.df["Doc. Verificar"].str.contains("revisar",na=False) |
            self.df["Clasificacion Banco"].str.contains("revisar",na=False)
        ].shape[0]
        monto_filas_rev=self.df[
            self.df["Doc. Verificar"].str.contains("revisar",na=False) |
            self.df["Clasificacion Banco"].str.contains("revisar",na=False)
        ]["IMPORTE"].sum()
        num_filas_atipicos=self.df[self.df["IMPORTE"]>1500].shape[0]
        return num_filas,monto_filas,num_filas_rev,monto_filas_rev,num_filas_atipicos

    def ExportarDataFrame_bcp(self,file_path="export.xlsx"):
        if file_path=="" or file_path is None:
            raise ValueError(f"No se ha seleccionado un arhivo.")
        if self.df is None:
            raise ValueError("Aun no se ha cargado el archivo.")
        if self.df_bcp is None:
            raise ValueError("Aun no se ha procesado el archivo.")

        try:
            # if not file_path:
            #     return "❌ Exportación cancelada."
                
            self.df_bcp.to_excel(file_path, index=False)

            return f"✅ Archivo guardado en: {file_path}"
        except Exception as e:
            raise ValueError("Error al cargar el archivo")
            # print(f"Error al cargar el archivo: {e}")



    