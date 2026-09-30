"""Prepara un archivo privado para importar en Render, sin imprimir sus valores."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIREBASE_KEYS = (
    "VITE_FIREBASE_API_KEY", "VITE_FIREBASE_AUTH_DOMAIN", "VITE_FIREBASE_PROJECT_ID",
    "VITE_FIREBASE_STORAGE_BUCKET", "VITE_FIREBASE_MESSAGING_SENDER_ID", "VITE_FIREBASE_APP_ID",
)


def read_env(path):
    values = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main():
    frontend = read_env(ROOT / "frontend/.env")
    backend = read_env(ROOT / "backend/.env")
    values = {key: frontend.get(key, "") for key in FIREBASE_KEYS}
    if any(not values[key] for key in FIREBASE_KEYS):
        raise SystemExit("Falta completar la configuración Firebase en frontend/.env.")
    values.update({
        "ATLAS_ENV": "production",
        "ATLAS_FIREBASE_PROJECT_ID": values["VITE_FIREBASE_PROJECT_ID"],
        "ANTHROPIC_API_KEY": backend.get("ANTHROPIC_API_KEY", ""),
        "ANTHROPIC_MODEL": backend.get("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        "ATLAS_ASSISTANT_HOURLY_LIMIT": "200",
    })
    if not values["ANTHROPIC_API_KEY"]:
        raise SystemExit("Falta ANTHROPIC_API_KEY; el asistente no funcionaría en la demostración.")
    destination = ROOT / ".deploy/render.env"
    destination.parent.mkdir(exist_ok=True, mode=0o700)
    with os.fdopen(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as output:
        for key, value in values.items():
            if any(character in value for character in "\r\n"):
                raise ValueError("Una variable contiene saltos de línea.")
            output.write(f"{key}={value}\n")
    destination.chmod(0o600)
    print("Archivo privado listo: .deploy/render.env (no se sube a Git).")


if __name__ == "__main__":
    main()
