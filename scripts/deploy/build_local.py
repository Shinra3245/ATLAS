"""Compila exactamente la imagen de Render con la configuración Firebase local."""
import os
from pathlib import Path
import subprocess
import tempfile

from prepare_env import FIREBASE_KEYS, ROOT, read_env


def main():
    environment = os.environ.copy()
    values = read_env(ROOT / "frontend/.env")
    command = ["docker", "build", "--tag", "atlasgeo:deploy-check"]
    for key in FIREBASE_KEYS:
        environment[key] = values.get(key, "")
        command.extend(["--build-arg", key])
    command.append(".")
    # Las imágenes base son públicas. Evita depender del llavero de Docker del escritorio.
    with tempfile.TemporaryDirectory(prefix="atlas-docker-config-") as temporary:
        Path(temporary, "config.json").write_text("{}\n")
        environment["DOCKER_CONFIG"] = temporary
        subprocess.run(command, cwd=ROOT, env=environment, check=True)


if __name__ == "__main__":
    main()
