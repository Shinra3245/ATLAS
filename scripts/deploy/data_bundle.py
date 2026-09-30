"""Empaqueta o instala solo los cinco JSON consumidos por el motor, con SHA-256."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
FILES = ("analysis_units.json", "municipal_context.json", "sources_catalog.json", "layer_manifest.json", "manifest.json")


def verify_data(folder: Path) -> dict:
    for name in FILES:
        if not (folder / name).is_file():
            raise ValueError(f"Falta el dato de producción: {name}")
    manifest = json.loads((folder / "manifest.json").read_text())
    for name in FILES[:-1]:
        blob = (folder / name).read_bytes()
        expected = manifest["outputs"][name]
        if len(blob) != expected["bytes"] or hashlib.sha256(blob).hexdigest() != expected["sha256"]:
            raise ValueError(f"Integridad incorrecta: {name}")
    units = json.loads((folder / "analysis_units.json").read_text())
    if not units or len(units) != manifest["records"]:
        raise ValueError("El número de localidades no coincide con el manifiesto.")
    if {row["municipality"] for row in units} != {"Irapuato", "Celaya"}:
        raise ValueError("La cobertura del paquete no corresponde al MVP.")
    if any(row.get("is_test_fixture") for row in units):
        raise ValueError("No se pueden publicar fixtures.")
    return manifest


def pack(folder: Path, destination: Path) -> str:
    verify_data(folder)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output:
        with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as tar:
                for name in FILES:
                    content = (folder / name).read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(content)
                    info.mode = 0o644
                    tar.addfile(info, io.BytesIO(content))
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def install(blob: bytes, checksum: str, folder: Path) -> None:
    if hashlib.sha256(blob).hexdigest() != checksum:
        raise ValueError("SHA-256 del paquete incorrecto. Despliegue cancelado.")
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        members = tar.getmembers()
        if sorted(item.name for item in members) != sorted(FILES):
            raise ValueError("El paquete contiene archivos inesperados.")
        if any(not item.isfile() or item.size > 16_000_000 for item in members):
            raise ValueError("Tipo o tamaño de archivo inválido.")
        folder.mkdir(parents=True, exist_ok=True)
        for item in members:
            with tar.extractfile(item) as source:
                (folder / item.name).write_bytes(source.read())
    verify_data(folder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["pack", "install", "verify"])
    parser.add_argument("--folder", type=Path, default=ROOT / "data/processed/v1")
    parser.add_argument("--output", type=Path, default=ROOT / ".deploy/atlas-data-v1.tar.gz")
    parser.add_argument("--release", type=Path, default=ROOT / "deploy/data-release.json")
    args = parser.parse_args()
    if args.command == "pack":
        print(pack(args.folder, args.output))
    elif args.command == "install":
        release = json.loads(args.release.read_text())
        if not release["url"].startswith("https://github.com/Shinra3245/ATLAS/releases/download/"):
            raise ValueError("El origen del paquete debe ser una release de ATLAS.")
        with urllib.request.urlopen(release["url"], timeout=60) as response:
            blob = response.read(8_000_001)
        if len(blob) > 8_000_000:
            raise ValueError("Paquete demasiado grande.")
        install(blob, release["sha256"], args.folder)
        print("Datos instalados y verificados.")
    else:
        print(json.dumps({"status": "ok", "records": verify_data(args.folder)["records"]}))


if __name__ == "__main__":
    main()
