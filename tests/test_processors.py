import tempfile
import unittest
from pathlib import Path

import pandas as pd

from modules.adm_ncr_def.model import NcrBCPProcesor, NcrDefProcesor
from modules.fact_masivo_comercial.model import ProcesarComercial


class DefProcessorTests(unittest.TestCase):
    def setUp(self):
        self.processor = NcrDefProcesor()
        self.processor.df = pd.DataFrame(
            [
                {
                    "N° NOTA CRÉDITO": 12345,
                    "FECHA NCR": "2026-01-01",
                    "TIPO DOC.": "1",
                    "N° DOCUMENTO": "12345678",
                    "DNI/RUC": "12345678",
                    "NOMBRE CLIENTE/RAZÓN SOCIAL": "CLIENTE",
                    "IMPORTE": "150.50",
                    "FECHA REGISTRO DATOS": "2026-01-01",
                    "CUENTA TITULAR": "CLIENTE",
                    "N° CUENTA": "1234567890123",
                    "CCI": "",
                    "BANCO": "BANCO DE CREDITO DEL PERU",
                    "ESTADO": "Datos Bancarios",
                    "CORREO": "cliente@example.com",
                }
            ]
        )

    def test_numeric_credit_note_is_supported(self):
        self.processor.procesarDEF()
        self.assertEqual(self.processor.df.iloc[0]["DEF FORMATEADO"], "12345")
        self.assertEqual(self.processor.df.iloc[0]["Clasificacion Banco"], "C")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "def.xlsx"
            self.processor.ExportarDataFrame_def(output)
            self.assertTrue(output.is_file())

    def test_invalid_cci_is_marked_for_review(self):
        result = self.processor.clasificacionBanco("OTRO BANCO", "", "123")
        self.assertIn("revisar CCI", result)


class BcpProcessorTests(unittest.TestCase):
    def test_only_documented_required_columns_are_enough(self):
        processor = NcrBCPProcesor()
        processor.df = pd.DataFrame(
            [
                {
                    "Clasificacion Banco": "C",
                    "Cuenta Seleccionada": "1234567890123",
                    "Clasificacion Doc": "1",
                    "DNI/RUC": "12345678",
                    "NOMBRE CLIENTE/RAZÓN SOCIAL": "CLIENTE",
                    "IMPORTE": 100,
                    "DEF FORMATEADO": "123",
                }
            ]
        )
        processor.procesarBCP()
        self.assertEqual(len(processor.df_bcp), 2)
        self.assertEqual(processor.df_bcp.iloc[1]["Nro. del Documento"], "123")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bcp.xlsx"
            processor.ExportarDataFrame_bcp(output)
            self.assertTrue(output.is_file())


class CommercialProcessorTests(unittest.TestCase):
    def test_comment_is_optional_and_falls_back_to_description(self):
        processor = ProcesarComercial()
        processor.folio = 10
        processor.tc = 3.75
        processor.df = pd.DataFrame(
            [
                {
                    "RUC": 20123456789,
                    "GLOSA DE FACTURA": "Servicio técnico",
                    "MONEDA": "soles",
                    "VALOR DE VENTA": 100,
                    "TOTAL": 118,
                }
            ]
        )
        processor.ProcesarData()
        processor.CargaPlantilla()
        self.assertEqual(processor.df.iloc[0]["COMENTARIO"], "SERVICIO TECNICO")
        self.assertEqual(processor.cabecera[1]["FolioNumber"], 10)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sap.xlsx"
            processor.exportData(output)
            processor.exportTxt(Path(directory) / "sap.txt")
            self.assertTrue(output.is_file())
            self.assertTrue((Path(directory) / "sap_cabecera.txt").is_file())
            self.assertTrue((Path(directory) / "sap_detalle.txt").is_file())

    def test_column_aliases_are_normalized_when_reading_excel(self):
        processor = ProcesarComercial()
        source = pd.DataFrame(
            [
                {
                    "Nro RUC": "20123456789",
                    "Descripción factura": "Servicio",
                    "Divisa": "S/",
                    "Subtotal": 100,
                    "Monto total": 118,
                }
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.xlsx"
            source.to_excel(path, index=False, sheet_name="Datos")
            processor.CargarDataFrame(path, "Datos", 1, 3.75)
            processor.ProcesarData()
        self.assertEqual(processor.df.iloc[0]["CODIGO"], "C20123456789")


if __name__ == "__main__":
    unittest.main()
