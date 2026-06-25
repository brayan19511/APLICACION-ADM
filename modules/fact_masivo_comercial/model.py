from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd

from core.business_config import CommercialRules
from core.dataframe_schema import (
    clean_text,
    normalize_columns,
    numeric_series,
    require_columns,
)
from core.exceptions import ExportError, ValidationError
from core.model import BaseModel


COMMERCIAL_ALIASES = {
    "RUC": ("NUMERO RUC", "NRO RUC"),
    "COMENTARIO": ("COMENTARIOS", "GLOSA"),
    "GLOSA DE FACTURA": ("GLOSA FACTURA", "DESCRIPCION FACTURA"),
    "MONEDA": ("CURRENCY", "DIVISA"),
    "VALOR DE VENTA": ("VALOR VENTA", "SUBTOTAL"),
    "TOTAL": ("IMPORTE TOTAL", "MONTO TOTAL"),
}

COMMERCIAL_REQUIRED_COLUMNS = (
    "RUC",
    "GLOSA DE FACTURA",
    "MONEDA",
    "VALOR DE VENTA",
    "TOTAL",
)


def _sap_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").upper())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.replace("/", "").replace("\\", "")


class ProcesarComercial(BaseModel):
    def __init__(self, rules: CommercialRules | None = None):
        super().__init__()
        self.rules = rules or CommercialRules()
        self.cabecera: list[dict] = []
        self.detalle: list[dict] = []
        self.folio = 0
        self.tc = 0.0

    def getFilePath(self):
        return self.path

    def getDf(self):
        return self.df

    @staticmethod
    def get_sheet_names(file_path):
        if not file_path:
            raise ValidationError("No se ha seleccionado un archivo.")
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"El archivo '{path}' no existe.")
        try:
            return pd.ExcelFile(path).sheet_names
        except Exception as exc:
            raise ValidationError(f"No se pudieron leer las hojas: {exc}") from exc

    def CargarDataFrame(self, file_path, sheet_name, folio, tc):
        if not file_path:
            raise ValidationError("No se ha seleccionado un archivo.")
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"El archivo '{path}' no existe.")
        if sheet_name in (None, ""):
            raise ValidationError("Seleccione una hoja del archivo.")
        try:
            self.folio = int(folio)
            self.tc = float(tc)
        except (TypeError, ValueError) as exc:
            raise ValidationError("El folio y el tipo de cambio deben ser números.") from exc
        if self.folio <= 0 or self.tc <= 0:
            raise ValidationError("El folio y el tipo de cambio deben ser mayores que cero.")
        try:
            raw = pd.read_excel(path, sheet_name=sheet_name, dtype=object)
            self.df = normalize_columns(raw, COMMERCIAL_ALIASES)
            self.path = str(path.resolve())
        except ValidationError:
            raise
        except Exception as exc:
            self.path = None
            self.df = None
            raise ValidationError(f"No se pudo leer el archivo Excel: {exc}") from exc

    def validate_columns(self):
        require_columns(self.df, COMMERCIAL_REQUIRED_COLUMNS)

    def ProcesarData(self):
        self.validate_columns()
        assert self.df is not None
        if "COMENTARIO" not in self.df.columns:
            self.df["COMENTARIO"] = self.df["GLOSA DE FACTURA"]
        selected = (*COMMERCIAL_REQUIRED_COLUMNS, "COMENTARIO")
        self.df = self.df.loc[:, list(dict.fromkeys(selected))].copy()
        self.df["TOTAL"] = numeric_series(self.df["TOTAL"], "TOTAL")
        self.df["VALOR DE VENTA"] = numeric_series(
            self.df["VALOR DE VENTA"], "VALOR DE VENTA"
        )
        self.cargaColumnas()

    def cargaColumnas(self):
        assert self.df is not None
        ruc = clean_text(self.df["RUC"]).str.replace(r"\.0$", "", regex=True)
        valid_ruc = ruc.str.fullmatch(r"\d{11}")
        self.df["CODIGO"] = ruc.where(valid_ruc, "").apply(
            lambda value: f"C{value}" if value else "revisar"
        )
        self.df["MONEDA"] = clean_text(self.df["MONEDA"]).str.upper()
        self.df["COMENTARIO"] = clean_text(self.df["COMENTARIO"]).apply(_sap_text)
        fallback = clean_text(self.df["GLOSA DE FACTURA"]).apply(_sap_text)
        self.df["COMENTARIO"] = self.df["COMENTARIO"].where(
            self.df["COMENTARIO"].ne(""), fallback
        )
        self.df["GLOSA DE FACTURA"] = fallback
        self.df["CURRENCY"] = (
            self.df["MONEDA"].map(self.rules.currency_aliases).fillna("revisar")
        )
        self.df["CUENTA"] = (
            self.df["CURRENCY"]
            .map(self.rules.account_by_currency)
            .fillna("revisar")
        )
        pen_amount = self.df["TOTAL"].where(
            self.df["CURRENCY"].eq("S/"), self.df["TOTAL"] * self.tc
        )
        has_detraction = pen_amount.ge(self.rules.detraction_threshold_pen) & (
            self.df["CURRENCY"].isin(("S/", "US$"))
        )
        self.df["TIPDETRACCION"] = has_detraction.map({True: "SI", False: "NO"})
        self.df["CODDETRACCION"] = has_detraction.map(
            {True: self.rules.detraction_code, False: "0"}
        )
        percentage = str(round(self.rules.detraction_rate * 100))
        self.df["PERDETRACCION"] = has_detraction.map(
            {True: percentage, False: "0"}
        )
        self.df["VALDETRACCION"] = (
            pen_amount.where(has_detraction, 0) * self.rules.detraction_rate
        ).round(4)

    def calcular_detraccion(self, tipdetra, moneda, total):
        if tipdetra != "SI":
            return 0
        amount = float(total) if moneda == "S/" else float(total) * self.tc
        return round(amount * self.rules.detraction_rate, 4)

    def analizarData(self):
        if self.df is None:
            raise ValidationError("Aún no se ha procesado un archivo.")
        review = (
            self.df["CURRENCY"].eq("revisar")
            | self.df["CUENTA"].eq("revisar")
            | self.df["CODIGO"].eq("revisar")
        )
        return (
            int(review.sum()),
            len(self.df),
            int(self.df["CURRENCY"].eq("S/").sum()),
            int(self.df["CURRENCY"].eq("US$").sum()),
            self.df["TOTAL"].sum(),
            self.df.loc[self.df["CURRENCY"].eq("S/"), "TOTAL"].sum(),
            self.df.loc[self.df["CURRENCY"].eq("US$"), "TOTAL"].sum(),
        )

    def CargaPlantilla(self):
        if self.df is None:
            raise ValidationError("Aún no se ha procesado un archivo.")
        self.cabecera = [
            {
                "DocNum": "Correlativo",
                "CardCode": "Codigo de Cliente",
                "DocType": "DATO POR DEFECTO",
                "ControlAccount": "Cuenta Comntable",
                "DocDate": "Fecha de cierre contable  (Formato: AAAAMMDD)",
                "DocDueDate": "Fecha de  Vencimiento (Formato: AAAAMMDD)",
                "DocCurrency": "Moneda Extranjera, si es SOLES no aplica",
                "TaxDate": "Fecha Emision de  Documento (Formato: AAAAMMDD)",
                "Indicator": "Tipo de Documento Sunat - Ver tabla",
                "FolioPrefixString": "Serie  Documento",
                "FolioNumber": "Correlativo Documento",
                "Comments": "Comentarios",
                "Series": "Series",
                "JournalMemo": "JrnlMemo",
                "U_RP_DETRAC": "Tiene Detracción?",
                "U_RP_COD_DETRACCION": "Codigo Detraccion",
                "U_RP_VAL_DETRA": "Valor Detraccion",
                "U_MSSL_PDT": "Porcentaje",
                "PaymentGroupCode": "GroupNum",
            }
        ]
        self.detalle = [
            {
                "ParentKey": "Correlativo",
                "LineNum": "Secuencia",
                "U_MSS_SERVEN": "U_MSS_SERVEN",
                "ItemDescription": "Descripcion factura",
                "PriceAfterVAT": "Saldo del Documento INC IGV",
                "AccountCode": "Cuenta Contable Carga",
                "CostingCode": "",
                "CostingCode3": "",
                "CostingCode4": "",
                "TaxCode": "ESTANDAR",
            }
        ]
        today = pd.Timestamp.today().strftime("%Y%m%d")
        due_date = (
            pd.Timestamp.today() + pd.DateOffset(days=self.rules.due_days)
        ).strftime("%Y%m%d")
        for sequence, row in enumerate(
            self.df.reset_index(drop=True).to_dict("records"), start=1
        ):
            self.cabecera.append(
                {
                    "DocNum": sequence,
                    "CardCode": row["CODIGO"],
                    "DocType": "dDocument_Service",
                    "ControlAccount": row["CUENTA"],
                    "DocDate": today,
                    "DocDueDate": due_date,
                    "DocCurrency": row["CURRENCY"],
                    "TaxDate": today,
                    "Indicator": "01",
                    "FolioPrefixString": self.rules.folio_prefix,
                    "FolioNumber": self.folio + sequence - 1,
                    "Comments": row["COMENTARIO"],
                    "Series": self.rules.series,
                    "JournalMemo": row["COMENTARIO"],
                    "U_RP_DETRAC": row["TIPDETRACCION"],
                    "U_RP_COD_DETRACCION": row["CODDETRACCION"],
                    "U_RP_VAL_DETRA": row["VALDETRACCION"],
                    "U_MSSL_PDT": row["PERDETRACCION"],
                    "PaymentGroupCode": self.rules.payment_group_code,
                }
            )
            self.detalle.append(
                {
                    "ParentKey": sequence,
                    "LineNum": "1",
                    "U_MSS_SERVEN": self.rules.service_code,
                    "ItemDescription": row["GLOSA DE FACTURA"],
                    "PriceAfterVAT": row["TOTAL"],
                    "AccountCode": self.rules.revenue_account,
                    "CostingCode": self.rules.costing_code,
                    "CostingCode3": "",
                    "CostingCode4": "",
                    "TaxCode": self.rules.tax_code,
                }
            )

    def exportData(self, file_path):
        if not file_path:
            raise ValidationError("No se ha seleccionado una ruta de salida.")
        if not self.cabecera or not self.detalle:
            raise ValidationError("Aún no se ha procesado un archivo.")
        try:
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                pd.DataFrame(self.cabecera).to_excel(
                    writer, sheet_name="cabecera", index=False
                )
                pd.DataFrame(self.detalle).to_excel(
                    writer, sheet_name="detalle", index=False
                )
            return f"✅ Archivo guardado en: {file_path}"
        except Exception as exc:
            raise ExportError(f"No se pudo exportar el archivo: {exc}") from exc

    def exportTxt(self, file_path):
        if not file_path:
            raise ValidationError("No se ha seleccionado una ruta de salida.")
        if not self.cabecera or not self.detalle:
            raise ValidationError("Aún no se ha procesado un archivo.")
        base_name = str(Path(file_path).with_suffix(""))
        header_path = f"{base_name}_cabecera.txt"
        detail_path = f"{base_name}_detalle.txt"
        try:
            pd.DataFrame(self.cabecera).to_csv(
                header_path, sep="\t", index=False, encoding="utf-8-sig"
            )
            pd.DataFrame(self.detalle).to_csv(
                detail_path, sep="\t", index=False, encoding="utf-8-sig"
            )
            return f"✅ Archivos guardados en:\n- {header_path}\n- {detail_path}"
        except Exception as exc:
            raise ExportError(f"No se pudieron exportar los TXT: {exc}") from exc
