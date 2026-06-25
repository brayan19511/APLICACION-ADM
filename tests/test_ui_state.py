import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from modules.adm_ncr_def.adm_bcp_view import AdmBCPView
from modules.adm_ncr_def.adm_def_view import AdmDefView
from modules.fact_masivo_comercial.view import FacturaMasivoComercialView


class ViewStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def assert_processing_state(self, view, export_buttons):
        self.assertTrue(view.load_button.isEnabled())
        for button in export_buttons:
            self.assertTrue(button.isEnabled())

        view.set_processed(True)
        for button in export_buttons:
            self.assertTrue(button.isEnabled())

        view.set_busy(True)
        self.assertFalse(view.load_button.isEnabled())
        self.assertFalse(view.upload_file_widget.browse_button.isEnabled())
        for button in export_buttons:
            self.assertFalse(button.isEnabled())

        view.set_busy(False)
        self.assertTrue(view.load_button.isEnabled())
        self.assertTrue(view.upload_file_widget.browse_button.isEnabled())
        for button in export_buttons:
            self.assertTrue(button.isEnabled())

        view.set_processed(False)
        for button in export_buttons:
            self.assertTrue(button.isEnabled())

    def assert_export_without_data_warns(self, view, request_export):
        messages = []
        view.show_message = lambda message, title, msg_type: messages.append(
            (message, title, msg_type)
        )
        request_export()
        self.assertEqual(len(messages), 1)
        self.assertIn("Primero debe cargar", messages[0][0])

    def test_def_button_states(self):
        view = AdmDefView()
        self.assert_processing_state(view, [view.export_button])
        self.assert_export_without_data_warns(view, view._request_export)

    def test_bcp_button_states(self):
        view = AdmBCPView()
        self.assert_processing_state(view, [view.export_button])
        self.assert_export_without_data_warns(view, view._request_export)

    def test_commercial_button_states(self):
        view = FacturaMasivoComercialView()
        self.assert_processing_state(view, [view.excel_button, view.txt_button])
        self.assert_export_without_data_warns(view, view._request_excel)
        self.assert_export_without_data_warns(view, view._request_txt)


if __name__ == "__main__":
    unittest.main()
