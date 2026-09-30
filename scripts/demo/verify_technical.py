"""Cierra la verificación técnica reproducible de datos, motor y API.

No modifica frontend ni reinicia la API de otra sesión. Ejecutar desde ATLAS:
    python3 scripts/demo/verify_technical.py
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/evidence/technical_verification.json')
    args = parser.parse_args()
    phases: list[dict] = []

    def execute(name: str, command: list[str]) -> bool:
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=240)
            phase = {'phase': name, 'status': 'PASS' if result.returncode == 0 else 'FAIL',
                     'exit_code': result.returncode,
                     'command': command,
                     'output_tail': (result.stdout + result.stderr)[-5000:]}
        except (OSError, subprocess.TimeoutExpired) as exc:
            phase = {'phase': name, 'status': 'FAIL', 'command': command, 'detail': str(exc)}
        phases.append(phase)
        print(phase['status'], name, flush=True)
        return phase['status'] == 'PASS'

    data_tests = 0
    code_tests = 0
    http_checks = 0
    with tempfile.TemporaryDirectory(prefix='atlas-tests-') as temp:
        data_ok = execute('datos: reconstrucción, integridad y pruebas',
                          [sys.executable, 'scripts/data/verify_v1.py'])
        if data_ok:
            data = json.loads((ROOT/'data/metadata/validation_report.json').read_text())
            # The data verifier owns the exact unittest log and original hashes.
            import re
            matched = re.search(r'Ran (\d+) tests', data['test_output'])
            data_tests = int(matched.group(1)) if matched else 0
            xml_path = Path(temp)/'tests.xml'
            code_ok = execute('motor y API: pruebas de contratos y regresión', [
                str(ROOT/'backend/.venv/bin/python'), '-m', 'pytest', 'tests/engine', 'tests/api',
                '-q', '-p', 'no:cacheprovider', f'--junitxml={xml_path}',
            ])
            if xml_path.exists():
                code_tests = len(ET.parse(xml_path).getroot().findall('.//testcase'))
            if code_ok:
                api_ok = execute('API: recorrido por HTTP real con instancia aislada',
                                 [sys.executable, 'scripts/demo/verify_api.py', '--launch'])
                if api_ok:
                    api = json.loads((ROOT/'docs/evidence/api_verification.json').read_text())
                    http_checks = len(api['checks'])
        report = {
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'status': 'PASS' if len(phases) == 3 and all(p['status'] == 'PASS' for p in phases) else 'FAIL',
            'scope': 'Datos publicados, motor, API y HTTP. Frontend y validación profesional excluidos.',
            'data_tests': data_tests, 'engine_api_tests': code_tests,
            'total_automated_tests': data_tests + code_tests, 'http_checks': http_checks,
            'phases': phases,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(args.output)
    print(report['status'], f'{report["total_automated_tests"]} pruebas; {http_checks} comprobaciones HTTP;', args.output)
    if report['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
