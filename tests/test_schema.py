import unittest

import pandas as pd

from core.dataframe_schema import normalize_columns, normalize_header
from core.exceptions import ValidationError


class SchemaTests(unittest.TestCase):
    def test_headers_ignore_accents_punctuation_and_spaces(self):
        self.assertEqual(
            normalize_header("  N° Nota Crédito  "),
            normalize_header("NRO NOTA CREDITO"),
        )

    def test_duplicate_aliases_are_rejected(self):
        dataframe = pd.DataFrame(columns=["Correo", "Correo "])
        with self.assertRaises(ValidationError):
            normalize_columns(dataframe, {"CORREO": ("EMAIL",)})


if __name__ == "__main__":
    unittest.main()
