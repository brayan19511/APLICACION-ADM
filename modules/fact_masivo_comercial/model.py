import os
from  core.model import BaseModel
import pandas as pd
import numpy as np

class ProcesarComercial(BaseModel):
    def __init__(self):
        super().__init__()
        self.cabecera=[]
        self.detalle=[]
    
    def getFilePath(self):
        return self.path
    def getDf(self):
        return self.df
    
    def CargarDataFrame(self,file_path,sheet_name,folio,tc):
        if file_path=="" or file_path is None:
            raise ValueError(f"No se ha seleccionado un arhivo.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo '{file_path}' no existe.")
        if folio=="" or tc=="":
            raise ValueError(f"Por favor complete todos los campos")
        try:
            # if self.df is not None:
            #     self.df=None
            self.path=file_path
            self.folio=folio
            self.tc=tc
            self.df:pd.DataFrame= pd.read_excel( file_path, sheet_name=sheet_name )

        except Exception as e:
            self.path=""
            self.df=None
            raise ValueError(f"❌ Error al exportar el archivo: {str(e)}")
    def validate_columns(self):
        REQUIREMENT_COLUMNS=['RUC','GLOSA DE FACTURA','MONEDA','VALOR DE VENTA','TOTAL' ]
        
        missing_columns = [col for col in REQUIREMENT_COLUMNS if col not in self.df.columns]
        
        if missing_columns:
            self.df=None
            raise ValueError(f"❌ Faltan las siguientes columnas: {', '.join(missing_columns)}")

    def ProcesarData(self):
        self.df=self.df[['RUC','COMENTARIO','GLOSA DE FACTURA','MONEDA','VALOR DE VENTA','TOTAL']]
        self.cargaColumnas()

    def cargaColumnas(self):
        validacionMoneda=   {
                "SOL":"S/",
                "SOLES":"S/",
                "S/.":"S/",
                "S":"S/",
                "S/":"S/",
                "DOL":"US$",
                "DOLARES":"US$",
                "$":"US$",
                "US$":"US$"
            }
        validacionTexto=str.maketrans({
            "Ñ":"N",
            "/":"",
            "\\":"",
            "Á":"A",
            "É":"E",
            "Í":"I",
            "Ó":"O",
            "Ú":"U"

        })
        self.df["CODIGO"]=self.df["RUC"].apply(lambda x: f"C{int(x)}" if pd.notna(x) and str(x).strip()!="" else "revisar")
        self.df["MONEDA"]=self.df["MONEDA"].str.upper()
        if "COMENTARIO" not in self.df.columns:
            self.df["COMENTARIO"] = self.df["GLOSA DE FACTURA"]
        self.df["COMENTARIO"]=self.df["COMENTARIO"].str.upper()
        self.df["GLOSA DE FACTURA"]=self.df["GLOSA DE FACTURA"].str.upper()
        self.df["COMENTARIO"]=self.df["COMENTARIO"].apply(lambda x : x.translate(validacionTexto))
        self.df["GLOSA DE FACTURA"]=self.df["GLOSA DE FACTURA"].apply(lambda x : x.translate(validacionTexto))
        self.df["CURRENCY"]=self.df["MONEDA"].map(validacionMoneda).fillna("revisar")
        self.df["CUENTA"]=self.df["CURRENCY"].apply(lambda x: "121210170" if x=="S/" else "121210230" if x == "US$" else "revisar")
        self.df["TIPDETRACCION"]=self.df.apply(lambda row :   "SI" if
                                                        (row["CURRENCY"]=="US$" and row["TOTAL"]*self.tc>=700) or   
                                                        (row["CURRENCY"]=="S/"  and row["TOTAL"]>=700)
                                                    else "NO"   
                                    ,axis=1
                                    )
        self.df["CODDETRACCION"]=self.df["TIPDETRACCION"].apply(lambda x : "022" if x=="SI" else "0")
        self.df["PERDETRACCION"]=self.df["TIPDETRACCION"].apply(lambda x : "12" if x=="SI" else "0")

        self.df["VALDETRACCION"]=self.df.apply(lambda row : self.calcular_detraccion(row["TIPDETRACCION"],row["CURRENCY"],row["TOTAL"]),axis=1)
        # C20300263578 037 PENDIENTE CROOSDOCKING


    
    def calcular_detraccion(self,tipdetra,moneda, total):
        if tipdetra =='SI'and moneda == "S/":
            return round(total * 0.12,4)
        elif tipdetra =='SI'and moneda == "US$":
            return round(total * 0.12 * self.tc,4)
        else:
            return 0  # Para otros casos
    def analizarData(self):
        filasrev,doc,docsol,docdol,monto,montosol,montodol=0,0,0,0,0,0,0
        filasrev=self.df[
            self.df["CURRENCY"].str.contains("revisar",na=False) |
            self.df["CUENTA"].str.contains("revisar",na=False)   |
            self.df["CODIGO"].str.contains("revisar",na=False)
        ].shape[0]
        doc=self.df.shape[0]
        docsol=self.df[self.df["CURRENCY"]=="S/"].shape[0]
        docdol=self.df[self.df["CURRENCY"]=="US$"].shape[0]
        monto=self.df["TOTAL"].sum()
        montosol=self.df[self.df["CURRENCY"]=="S/"]["TOTAL"].sum()
        montodol=self.df[self.df["CURRENCY"]=="US$"]["TOTAL"].sum()
        return filasrev,doc,docsol,docdol,monto,montosol,montodol

    def CargaPlantilla(self):
        self.cabecera=[]
        self.detalle=[]
        fecha1=pd.Timestamp.today().strftime("%Y%m%d")
        fecha2=(pd.Timestamp.today()+pd.DateOffset(days=30)).strftime("%Y%m%d")

        lastfolio=self.folio

        cab={
            "DocNum"                :"Correlativo",
            "CardCode"             :"Codigo de Cliente",
            "DocType"              :"DATO POR DEFECTO",
            "ControlAccount"       :"Cuenta Comntable",
            "DocDate"              :"Fecha de cierre contable  (Formato: AAAAMMDD)",
            "DocDueDate"           :"Fecha de  Vencimiento (Formato: AAAAMMDD)",
            "DocCurrency"          :"Moneda Extranjera, si es SOLES no aplica",
            "TaxDate"              :"Fecha Emision de  Documento (Formato: AAAAMMDD)",
            "Indicator"            :"Tipo de Documento Sunat - Ver tabla",
            "FolioPrefixString"    :"Serie  Documento",
            "FolioNumber"          :"Correlativo Documento",
            "Comments"             :"Comentarios",
            "Series"               :"Series",
            "JournalMemo"          :"JrnlMemo",
            "U_RP_DETRAC"          :"Tiene Detracción?",
            "U_RP_COD_DETRACCION"  :"Codigo Detraccion",
            "U_RP_VAL_DETRA"       :"Valor Detraccion",
            "U_MSSL_PDT"           :"Porcentaje",
            "PaymentGroupCode"     :"GroupNum"
            }
        self.cabecera.append(cab)
        det={
                'ParentKey':"Correlativo",
                'LineNum':"Secuencia",
                'U_MSS_SERVEN':"U_MSS_SERVEN",
                'ItemDescription':"DescripciOn factura",
                'PriceAfterVAT':"Saldo del Documento INC IGV",
                'AccountCode':"Cuenta Contable Carga",
                'CostingCode':"",
                'CostingCode3':"",
                'CostingCode4':"",
                'TaxCode':"ESTANDAR"
            }
        self.detalle.append(det)

        for index,row in self.df.iterrows():
            cab={
            "DocNum":index+1,
            "CardCode":row["CODIGO"],
            "DocType":"dDocument_Service",
            "ControlAccount":row["CUENTA"],
            "DocDate":fecha1,
            "DocDueDate":fecha2,
            "DocCurrency":row["CURRENCY"],
            "TaxDate":fecha1,
            "Indicator":"01",
            "FolioPrefixString":"F001",
            "FolioNumber":lastfolio+index,
            "Comments":row["COMENTARIO"],
            "Series":"161",
            "JournalMemo":row["COMENTARIO"],
            "U_RP_DETRAC":row["TIPDETRACCION"],
            "U_RP_COD_DETRACCION":row["CODDETRACCION"],
            "U_RP_VAL_DETRA":row["VALDETRACCION"],
            "U_MSSL_PDT":row["PERDETRACCION"],
            "PaymentGroupCode":"18"
            }
            self.cabecera.append(cab)
            det={
                'ParentKey':index+1,
                'LineNum':"1",
                'U_MSS_SERVEN':"SV0004",
                'ItemDescription':row["GLOSA DE FACTURA"],
                'PriceAfterVAT':row["TOTAL"],
                'AccountCode':"759600000",
                'CostingCode':"A0202000",
                'CostingCode3':"",
                'CostingCode4':"",
                'TaxCode':"IGV_18"
            }

            self.detalle.append(det)
        
    def exportData(self,file_path):
        if file_path=="" or file_path is None:
            raise ValueError(f"No se ha seleccionado un arhivo.")
        if self.df is None:
            raise ValueError("Aun no se ha cargado el archivo.")
        
        try:
            df_cab=pd.DataFrame(self.cabecera)
            df_det=pd.DataFrame(self.detalle)
            with pd.ExcelWriter(file_path,engine="openpyxl") as writer:
                df_cab.to_excel(writer,sheet_name="cabecera",index=False)
                df_det.to_excel(writer,sheet_name="detalle",index=False)
            return f"✅ Archivo guardado en: {file_path}"
        except Exception as e:
            raise ValueError("Error al exportar el archivo")
    def exportTxt(self, file_path):
        if not file_path:
            raise ValueError("No se ha seleccionado un archivo.")
        if self.df is None:
            raise ValueError("Aún no se ha cargado el archivo.")

        try:
            df_cab = pd.DataFrame(self.cabecera)
            df_det = pd.DataFrame(self.detalle)

            # Obtener la ruta y nombre base sin extensión
            base_name, _ = os.path.splitext(file_path)

            # Definir los nombres de los archivos TXT
            cabecera_txt = f"{base_name}_cabecera.txt"
            detalle_txt = f"{base_name}_detalle.txt"

            # Exportar cada DataFrame a su respectivo archivo TXT
            df_cab.to_csv(cabecera_txt, sep="\t", index=False)  # TXT separado por tabulador
            df_det.to_csv(detalle_txt, sep="\t", index=False)  # TXT separado por tabulador

            return f"✅ Archivos guardados en:\n- {cabecera_txt}\n- {detalle_txt}"
        except Exception as e:
            raise ValueError(f"Error al exportar los archivos: {e}")

    