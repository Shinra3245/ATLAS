"""Publica el contexto municipal de los cuatro libros de localidades.

Valida las copias inmutables de ``data/raw/municipal_context/``. El constructor
principal incluye esta extensión y sus hashes en la publicación V1. No modifica
los campos de ``analysis_units``. Los campos ``*_MUN_CONTEXT`` se conservan tal
cual: repetirlos por localidad no los convierte en una medición local.
"""

from __future__ import annotations

import math
from pathlib import Path

import openpyxl
from inspect_datasets import sha256

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "municipal_context"
OUTPUT = ROOT / "data" / "processed" / "v1" / "municipal_context.json"
UNITS = ROOT / "data" / "processed" / "v1" / "analysis_units.json"

BOOKS = (
    (
        "riesgos_naturales_localidades",
        "01_Riesgos_Naturales_Localidades_Celaya_Irapuato.xlsx",
        "Riesgos naturales por localidad (contexto municipal)",
    ),
    (
        "vulnerabilidad_resiliencia_localidades",
        "02_Vulnerabilidad_Resiliencia_Localidades_Celaya_Irapuato.xlsx",
        "Vulnerabilidad y resiliencia por localidad (contexto municipal)",
    ),
    (
        "riesgos_ambientales_localidades",
        "03_Riesgos_Ambientales_Localidades_Celaya_Irapuato.xlsx",
        "Riesgos ambientales por localidad (contexto municipal)",
    ),
    (
        "exposicion_riesgos_localidades",
        "04_Exposicion_Riesgos_Localidades_Celaya_Irapuato.xlsx",
        "Exposición por localidad (contexto municipal)",
    ),
)

IDENTITY = {"CVEGEO", "MUN", "NOM_MUN", "LOC", "NOM_LOC", "LONGITUD", "LATITUD"}
LIMITATION = (
    "Los campos terminados en _MUN_CONTEXT son indicadores municipales; "
    "repetirlos por localidad no los convierte en mediciones locales."
)


def _cell(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("MUNICIPAL_NON_FINITE: valor no finito en contexto municipal")
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _field_code(column: str, source_id: str) -> str:
    code = column.lower()
    if column == "NIVEL_FUENTE":
        return f"{code}_{source_id}"
    return code


def _locality_id(value: object) -> str:
    normalized = _cell(value)
    return str(normalized).strip()


def _load_sheet(path: Path) -> tuple[list[str], list[tuple]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(workbook["Localidades"].iter_rows(values_only=True))
    finally:
        workbook.close()
    if not rows:
        raise ValueError(f"MUNICIPAL_EMPTY: {path.name}")
    header = [str(cell) for cell in rows[0]]
    if len(header) != len(set(header)) or not IDENTITY.issubset(header):
        raise ValueError(f"MUNICIPAL_HEADER: columnas duplicadas o identidad incompleta: {path.name}")
    for column in set(header) - IDENTITY:
        if column != "NIVEL_FUENTE" and not column.upper().endswith("_MUN_CONTEXT"):
            raise ValueError(f"MUNICIPAL_FIELD_SCOPE: {path.name}/{column}")
    return header, rows[1:]


def build_context(units: list[dict], paths: dict[str, Path]) -> dict:
    """Valida identidad y resolución municipal antes de publicar cualquier campo.

    La unidad principal no se modifica. Las fuentes se leen desde las copias raw
    verificadas por build_v1 y los valores se mantienen como contexto municipal.
    """
    by_id = {str(row["id"]): row for row in units}
    if len(by_id) != len(units):
        raise ValueError("MUNICIPAL_MASTER_DUPLICATE: identidad duplicada en maestro")
    expected = set(by_id)
    values_by_id: dict[str, dict[str, object]] = {key: {} for key in sorted(expected)}
    fields: list[dict[str, str]] = []
    sources: list[dict[str, object]] = []
    field_codes: set[str] = set()

    for source_id, filename, title in BOOKS:
        path = paths[filename]
        header, rows = _load_sheet(path)
        index = {name: position for position, name in enumerate(header)}
        found = set()
        municipal_values: dict[tuple[str, str], object] = {}
        for row in rows:
            if all(cell is None for cell in row):
                continue
            locality_id = _locality_id(row[index["CVEGEO"]])
            if locality_id not in expected:
                raise ValueError(f"MUNICIPAL_OUTSIDE_MASTER: {filename}/{locality_id}")
            if locality_id in found:
                raise ValueError(f"MUNICIPAL_DUPLICATE: {filename}/{locality_id}")
            found.add(locality_id)
            unit = by_id[locality_id]
            identity = {
                "NOM_MUN": unit["municipality"],
                "NOM_LOC": unit["locality"],
                "MUN": int(unit["municipality_code"]),
                "LOC": int(unit["locality_code"]),
            }
            for column, expected_value in identity.items():
                if _cell(row[index[column]]) != expected_value:
                    raise ValueError(f"MUNICIPAL_IDENTITY_CONFLICT: {filename}/{locality_id}/{column}")
            for column, field in [("LONGITUD", "longitude"), ("LATITUD", "latitude")]:
                value = row[index[column]]
                if (not isinstance(value, (int, float)) or isinstance(value, bool)
                        or not math.isfinite(value)
                        or not math.isclose(value, unit[field], rel_tol=1e-12, abs_tol=1e-10)):
                    raise ValueError(f"MUNICIPAL_COORDINATE_CONFLICT: {filename}/{locality_id}/{column}")
            for column in header:
                if column in IDENTITY:
                    continue
                code = _field_code(column, source_id)
                value = _cell(row[index[column]])
                key = (unit["municipality"], column)
                if key in municipal_values and municipal_values[key] != value:
                    raise ValueError(f"MUNICIPAL_RESOLUTION_CONFLICT: {filename}/{key}")
                municipal_values[key] = value
                values_by_id[locality_id][code] = value
        if found != expected:
            missing = sorted(expected - found)
            raise ValueError(f"MUNICIPAL_MISSING: {filename}: faltan {len(missing)} claves, {missing[:5]}")
        for column in header:
            if column in IDENTITY:
                continue
            code = _field_code(column, source_id)
            if code in field_codes:
                raise ValueError(f"MUNICIPAL_FIELD_COLLISION: {code}")
            field_codes.add(code)
            fields.append(
                {
                    "code": code,
                    "column": column,
                    "label": column,
                    "source_id": source_id,
                }
            )
        sources.append(
            {
                "id": source_id,
                "name": title,
                "institution": "UNKNOWN",
                "dataset": f"data/incoming/new_downloads/{filename}",
                "date_or_version": "UNKNOWN",
                "coverage_note": "755 localidades de Irapuato y Celaya; valores constantes dentro de cada municipio.",
                "verification_status": "SOURCE_PROVENANCE_PARTIAL",
                "usage": "MUNICIPAL_CONTEXT",
                "limitations": LIMITATION,
                "sha256": sha256(path),
                "original_url": "UNKNOWN",
                "license_or_terms": "PENDING_SOURCE_PROVENANCE",
                "is_test_fixture": False,
            }
        )

    return {
        "limitation": LIMITATION,
        "sources": sources,
        "fields": fields,
        "values_by_id": values_by_id,
    }


def main() -> None:
    """Mantiene el comando anterior sin publicar una extensión fuera del manifiesto."""
    from build_v1 import main as publish_v1
    publish_v1()


if __name__ == "__main__":
    main()
