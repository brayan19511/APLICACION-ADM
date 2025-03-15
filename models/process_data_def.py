import numpy as np
import pandas as pd
class DefProcessor:


    def __init__(self,df:pd.DataFrame):
        self.df=df


        
    def clean_data(self)->pd.DataFrame:
        self.df = self.df[self.df["ESTADO"]=="Datos Bancarios"].copy()
        self.clasificacion()
        return self.df

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
        self.ajustarColumnas()
        
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


        df_plantillaBcp=pd.DataFrame(plantillaBcp)
        return df_plantillaBcp
    

