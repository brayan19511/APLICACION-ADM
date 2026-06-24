from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence

import pandas as pd

from core.exceptions import ValidationError


def normalize_header(value: object) -> str:
    """Convierte encabezados variables de Excel a una clave comparable."""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper().strip()
    text = text.replace("º", "°")
    text = re.sub(r"\bN°", "NRO", text)
    return re.sub(r"[^A-Z0-9]+", " ", text).strip()


def normalize_columns(
    dataframe: pd.DataFrame,
    aliases: Mapping[str, Sequence[str]],
) -> pd.DataFrame:
    """Renombra alias conocidos a nombres canónicos y detecta ambigüedades."""
    alias_index: dict[str, str] = {}
    for canonical, variants in aliases.items():
        for variant in (canonical, *variants):
            normalized = normalize_header(variant)
            previous = alias_index.get(normalized)
            if previous and previous != canonical:
                raise RuntimeError(
                    f"El alias '{variant}' está asociado a dos columnas internas."
                )
            alias_index[normalized] = canonical

    rename: dict[object, str] = {}
    destinations: dict[str, object] = {}
    for original in dataframe.columns:
        canonical = alias_index.get(normalize_header(original))
        if canonical is None:
            continue
        if canonical in destinations:
            raise ValidationError(
                f"Las columnas '{destinations[canonical]}' y '{original}' "
                f"representan el mismo dato ({canonical})."
            )
        destinations[canonical] = original
        rename[original] = canonical

    return dataframe.rename(columns=rename).copy()


def require_columns(dataframe: pd.DataFrame | None, columns: Sequence[str]) -> None:
    if dataframe is None:
        raise ValidationError("Aún no se ha cargado un archivo.")
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise ValidationError(
            "Faltan las siguientes columnas: " + ", ".join(missing)
        )


def clean_text(series: pd.Series) -> pd.Series:
    """Devuelve texto limpio sin convertir valores vacíos en 'nan'."""
    return series.astype("string").fillna("").str.strip()


def numeric_series(series: pd.Series, label: str) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    invalid = numeric.isna() & clean_text(series).ne("")
    if invalid.any():
        rows = ", ".join(str(index + 2) for index in series.index[invalid][:10])
        raise ValidationError(
            f"La columna '{label}' contiene valores no numéricos "
            f"(filas de Excel: {rows})."
        )
    return numeric.fillna(0)
