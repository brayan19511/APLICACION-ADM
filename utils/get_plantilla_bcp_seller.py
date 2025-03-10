import pandas as pd

class PlantillaBCP():
    def __init__(self,df:pd.DataFrame,textoDoc=None):
        self.df=df
        # self.textDoc=textoDoc
        self.df["DEF FORMATEADO"] = self.df["Ref1"] if textoDoc is None else textoDoc
    


    def proces_data_seller(self)->pd.DataFrame:
        self.clean_data()
        return self.getPlantillaBCP()

    def clean_data(self):
        self.df["BankNameSeleccionado"]=self.df["BankNameSeleccionado"].replace({
        "BANCO CENTRAL RESERVA DEL PERU": "BANCO DE CREDITO DEL PERU", 
        r".*\bBCP\b.*": "BANCO DE CREDITO DEL PERU"  # Reemplaza cualquier texto que contenga "BCP"
    }, regex=True)
        self.df["Cuenta Seleccionada"]=self.df["DflAccountSeleccionado"].replace("-",'',regex=True).str.strip()
        self.df["Clasificacion Banco"]=self.df.apply(lambda row: self.clasificacion_bank(row["BankNameSeleccionado"],row["Cuenta Seleccionada"]),axis=1)
        self.df["Clasificacion Doc"]=self.df["LicTradNum"].apply(self.clasificacionDoc)
      
    def clasificacionDoc(self,x):
        if len(x)==8:
            return "1"
        elif len(x)==9:
            return "3"
        elif len(x)==11:
            return "6"
        else:
            return "4"
    def clasificacion_bank(self,banco,cuenta):
        if str(banco)=='BANCO DE CREDITO DEL PERU':
            if len(cuenta)==13:
                return "C"
            elif len(cuenta)==14:
                return "A"
            else:
                return f"revisar BCP: {len(cuenta)} digitos"
        else:
            if len(cuenta)==20:
                return "B"
            else:
                f"revisar CIC: {len(cuenta)} digitos"
    def getPlantillaBCP(self)->pd.DataFrame:
        # df_plantilla=pd.read_excel('plantilla_lista.xlsx', dtype={'Cuenta Seleccionada': str,'DNI/RUC':str})
        plantillaBcp=[]


        for index,row in self.df.iterrows():

            fila1={
                "Tipo de Registro":"A",
                "Tipo de Cuenta de Abono":row["Clasificacion Banco"],
                "Cuenta de Abono":row["Cuenta Seleccionada"],
                "Tipo de Documento de Identidad":row["Clasificacion Doc"],
                "Número de Documento de Identidad":row["LicTradNum"],
                "Correlativo de Documento de Identidad":"",
                "Nombre del proveedor":row["CardName"],
                "Tipo de Moneda de Abono":"S",
                "Monto del Abono":row["Debit"],
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
                "Monto del Documento":row["Debit"]

            }

            plantillaBcp.append(fila1)
            plantillaBcp.append(fila2)


        df_plantillaBcp=pd.DataFrame(plantillaBcp)
        return df_plantillaBcp