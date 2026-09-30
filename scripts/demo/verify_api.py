"""Verificación por HTTP real del MVP, sin navegador ni servicios externos.

Ejecutar con --launch para crear y detener un Uvicorn propio en un puerto libre.
No modifica ni reinicia el proceso de API usado por otra sesión.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
PROJECT_TYPES = ('housing', 'building', 'road')
FORBIDDEN = {
    'winner', 'best_location', 'risk_score', 'global_risk', 'global_risk_score',
    'risk_percentage', 'safety_percentage', 'safety_score', 'feasibility_score',
    'feasibility_percentage', 'overall_risk', 'overall_risk_percent', 'ranking',
}


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def no_forbidden(value: object) -> None:
    if isinstance(value, dict):
        ensure(not FORBIDDEN.intersection(value), 'Resultado contiene puntuación o ganador prohibido')
        for item in value.values():
            no_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            no_forbidden(item)


def request(base: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body, allow_nan=False).encode() if body is not None else None
    req = Request(base + path, data=data, headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(req, timeout=10)
    except HTTPError as exc:
        response = exc
    with response:
        return response.status, json.loads(response.read())


def location(catalog: list[dict], locality_id: str) -> dict:
    row = next(item for item in catalog if item['id'] == locality_id)
    return {'lat': row['latitude'], 'lon': row['longitude'], 'locality_id': row['id']}


def factors(result: dict) -> dict[str, dict]:
    rows = [*result['conditions'], *result['territorial_factors'], *result['context']]
    ensure(len(rows) == len({row['factor'] for row in rows}), 'Factores duplicados en ficha')
    return {row['factor']: row for row in rows}


def verify(base: str) -> dict:
    checks: list[dict] = []
    summary: dict = {}
    analyses: dict = {}

    def check(name, action):
        try:
            action()
        except Exception as exc:
            checks.append({'check': name, 'status': 'FAIL', 'detail': str(exc)})
        else:
            checks.append({'check': name, 'status': 'PASS'})

    def catalog_check():
        for path in ['/health', '/meta', '/locations', '/layers', '/sources', '/ml/status']:
            status, result = request(base, '/api' + path)
            ensure(status == 200, f'{path}: HTTP {status}')
            no_forbidden(result)
            summary[path] = result
        ensure(summary['/health']['status'] == 'ok', 'Salud incorrecta')
        ensure(summary['/meta']['project_types'] == list(PROJECT_TYPES), 'Tipos de obra distintos')
        ensure(set(summary['/meta']['supported_municipalities']) == {'Irapuato', 'Celaya'}, 'Cobertura distinta del MVP')
        ensure(len(summary['/locations']['locations']) == 755, 'Catálogo no contiene 755 localidades')
        ensure(summary['/ml/status']['enabled'] is False, 'ML activado sin validación')
        ensure(len(summary['/sources']['sources']) == 14, 'Catálogo de fuentes incompleto')
        for source in summary['/sources']['sources']:
            ensure(source.get('is_test_fixture') is not True, 'Fuente de prueba publicada')
            ensure(source['verification_status'] == 'SOURCE_PROVENANCE_PARTIAL', 'Procedencia parcial no visible')

    check('catálogos reales y alcance', catalog_check)
    catalog = summary.get('/locations', {}).get('locations', [])

    def analyze_check(project_type):
        for key, locality_id in [('a', '110070078'), ('b', '110170001')]:
            body = {'project_type': project_type, 'location': location(catalog, locality_id)}
            status, result = request(base, '/api/analyze', body)
            ensure(status == 200, f'Análisis {key}: HTTP {status}')
            ensure(result['schema_version'] == 'engine_result/v1', 'Contrato de análisis distinto')
            ensure(result['location']['locality_id'] == locality_id, 'Identidad de localidad incorrecta')
            ensure(result['project_type'] == project_type, 'Tipo de obra alterado')
            no_forbidden(result)
            rows = factors(result)
            ensure(result['coverage']['expected'] == len(rows), 'Cobertura no coincide con factores')
            states = Counter(row['status'] for row in rows.values())
            for name in ['data_available', 'partial_data', 'insufficient_data',
                         'no_registered_condition', 'blocked_data_validation']:
                ensure(result['coverage'][name] == states[name.upper()], f'Conteo incorrecto: {name}')
            for name in ['faults', 'landslide_susceptibility', 'land_use']:
                ensure(rows[name]['status'] == 'INSUFFICIENT_DATA', f'Capa pendiente publicada: {name}')
            ensure(rows['slope']['status'] == 'BLOCKED_DATA_VALIDATION', 'Pendiente no validada utilizada')
            for row in rows.values():
                ensure(bool(row['explanation']['not_meaning']), 'Falta explicación de alcance')
                if '_mun_context' in row['factor']:
                    ensure(row['category'] == 'context' and row['status'] == 'PARTIAL_DATA', 'Indicador municipal convertido a amenaza local')
            ensure(result['ml']['enabled'] is False, 'Ficha requiere ML')
            again_status, again = request(base, '/api/analyze', body)
            ensure(again_status == 200 and result == again, 'Análisis no determinista')
            analyses[(project_type, key)] = result

    def compare_check(project_type):
        status, result = request(base, '/api/compare', {
            'project_type': project_type,
            'location_a': location(catalog, '110070078'),
            'location_b': location(catalog, '110170001'),
        })
        ensure(status == 200, f'Comparación: HTTP {status}')
        no_forbidden(result)
        left = factors(analyses[(project_type, 'a')])
        right = factors(analyses[(project_type, 'b')])
        ensure(set(left) == set(right) == {row['factor'] for row in result['factors']}, 'A/B usa criterios distintos')
        for row in result['factors']:
            name = row['factor']
            ensure(row['value_a'] == left[name]['value'] and row['value_b'] == right[name]['value'], f'Valor A/B alterado: {name}')
            ensure(row['status_a'] == left[name]['status'] and row['status_b'] == right[name]['status'], f'Estado A/B alterado: {name}')
        ensure(result['coverage_a'] == analyses[(project_type, 'a')]['coverage'], 'Cobertura A alterada')
        ensure(result['coverage_b'] == analyses[(project_type, 'b')]['coverage'], 'Cobertura B alterada')

    for project_type in PROJECT_TYPES:
        check(f'fichas y determinismo: {project_type}', lambda p=project_type: analyze_check(p))
        check(f'comparación A/B: {project_type}', lambda p=project_type: compare_check(p))

    def invariant_check():
        reference = factors(analyses[('housing', 'a')])
        for project_type in ['building', 'road']:
            current = factors(analyses[(project_type, 'a')])
            for name, row in reference.items():
                for field in ['value', 'unit', 'status', 'category', 'temporal_context', 'source']:
                    ensure(row[field] == current[name][field], f'Tipo de obra cambia dato: {name}/{field}')
        ensure(reference['flood_history']['temporal_context'] == 'historical', 'Inundación histórica presentada como actual')
        ensure(reference['elevation']['temporal_context'] == 'reference_period', 'Altitud censal presentada como actual')

    check('invariancia de datos y temporalidad por tipo de obra', invariant_check)

    def history_check():
        for locality_id, expected in [('110070078', 'DATA_AVAILABLE'),
                                      ('110070079', 'NO_REGISTERED_CONDITION'),
                                      ('110170001', 'INSUFFICIENT_DATA')]:
            status, result = request(base, '/api/analyze', {
                'project_type': 'housing', 'location': location(catalog, locality_id),
            })
            ensure(status == 200 and factors(result)['flood_history']['status'] == expected, f'Interpretación histórica incorrecta: {locality_id}')
    check('antecedente positivo, sin registro y dato ausente', history_check)

    def expected_error(path, body, status_code, code):
        status, result = request(base, path, body)
        ensure(status == status_code and result.get('error') == code, f'{path}: se esperaba {status_code}/{code}; llegó {status}/{result.get("error")}')

    check('fuera de cobertura', lambda: expected_error('/api/analyze', {
        'project_type': 'housing', 'location': {'lat': 19.4326, 'lon': -99.1332},
    }, 422, 'OUTSIDE_SUPPORTED_AREA'))
    check('clave inexistente', lambda: expected_error('/api/analyze', {
        'project_type': 'housing', 'location': {'lat': 0, 'lon': 0, 'locality_id': '999999999'},
    }, 404, 'NOT_FOUND'))
    check('coordenada inválida', lambda: expected_error('/api/analyze', {
        'project_type': 'housing', 'location': {'lat': 91, 'lon': 0},
    }, 422, 'VALIDATION_ERROR'))
    same = {'lat': 0, 'lon': 0, 'locality_id': '110070078'}
    check('comparación de misma localidad', lambda: expected_error('/api/compare', {
        'project_type': 'housing', 'location_a': same, 'location_b': same,
    }, 422, 'SAME_LOCATION'))

    def key_check():
        status, result = request(base, '/api/compare', {
            'project_type': 'building', 'location_a': same,
            'location_b': {'lat': 0, 'lon': 0, 'locality_id': '110170001'},
        })
        ensure(status == 200, 'Comparación por clave rechazada por coordenadas auxiliares')
        ensure(result['location_a']['locality_id'] != result['location_b']['locality_id'], 'Claves distintas resueltas a misma localidad')
    check('selección por clave autoritativa', key_check)

    return {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if all(check['status'] == 'PASS' for check in checks) else 'FAIL',
        'transport': 'real_http', 'base_url': base,
        'scope': 'API y motor con datos publicados; no certifica frontend ni dictamen territorial',
        'locations': len(catalog),
        'sources': len(summary.get('/sources', {}).get('sources', [])),
        'checks': checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--launch', action='store_true', help='Inicia una API propia en un puerto libre y la detiene al terminar')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/evidence/api_verification.json')
    args = parser.parse_args()
    process = None
    log = None
    try:
        base = args.base_url.rstrip('/')
        if args.launch:
            with socket.socket() as reserve:
                reserve.bind(('127.0.0.1', 0))
                port = reserve.getsockname()[1]
            base = f'http://127.0.0.1:{port}'
            log = tempfile.TemporaryFile(mode='w+b')
            process = subprocess.Popen([
                str(ROOT/'backend/.venv/bin/python'), '-m', 'uvicorn', 'app.main:app',
                '--host', '127.0.0.1', '--port', str(port),
            ], cwd=ROOT/'backend', stdout=log, stderr=log)
            deadline = time.monotonic() + 15
            while True:
                if process.poll() is not None:
                    log.seek(0)
                    raise RuntimeError('API aislada no inició: ' + log.read().decode(errors='replace')[-2000:])
                try:
                    status, _ = request(base, '/api/health')
                    if status == 200:
                        break
                except (URLError, TimeoutError):
                    pass
                if time.monotonic() >= deadline:
                    raise RuntimeError('La API aislada no respondió en 15 segundos')
                time.sleep(0.1)
        report = verify(base)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(args.output)
        for item in report['checks']:
            print(item['status'], item['check'], item.get('detail', ''))
        print(report['status'], args.output)
        if report['status'] != 'PASS':
            raise SystemExit(1)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if log is not None:
            log.close()


if __name__ == '__main__':
    main()
