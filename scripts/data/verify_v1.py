"""Rebuild V1 and check determinism, original preservation and contract tests."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

from inspect_datasets import sha256

ROOT = Path(__file__).resolve().parents[2]


def hashes(folder):
    return {str(p.relative_to(ROOT)): sha256(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def main():
    original_before = {**hashes(ROOT/'data/incoming'), **hashes(ROOT/'data/raw')}
    products_before = hashes(ROOT/'data/processed/v1')
    # Only the publication timestamp may change on a deterministic rebuild.
    manifest_before = json.loads((ROOT/'data/processed/v1/manifest.json').read_text())
    subprocess.run([sys.executable, 'scripts/data/build_v1.py'], cwd=ROOT, check=True)
    products_after = hashes(ROOT/'data/processed/v1')
    manifest_after = json.loads((ROOT/'data/processed/v1/manifest.json').read_text())
    for manifest in (manifest_before, manifest_after):
        manifest.pop('generated_at', None)
    manifest_path = 'data/processed/v1/manifest.json'
    products_before.pop(manifest_path)
    products_after.pop(manifest_path)
    assert products_before == products_after, 'NON_DETERMINISTIC_OUTPUT'
    assert manifest_before == manifest_after, 'NON_DETERMINISTIC_MANIFEST'
    assert original_before == {**hashes(ROOT/'data/incoming'), **hashes(ROOT/'data/raw')}, 'ORIGINAL_CHANGED'
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/data', '-v'],
                           cwd=ROOT, capture_output=True, text=True)
    print(tests.stdout, end='')
    print(tests.stderr, end='')
    report = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS' if tests.returncode == 0 else 'FAIL',
        'originals_unchanged': True,
        'deterministic_outputs': True,
        'deterministic_manifest_excluding_generated_at': True,
        'originals_checked': len(original_before),
        'output_hashes': products_after,
        'test_command': f'{sys.executable} -m unittest discover -s tests/data -v',
        'test_exit_code': tests.returncode,
        'test_output': tests.stdout + tests.stderr,
    }
    report_path = ROOT/'data/metadata/validation_report.json'
    temporary = report_path.with_suffix('.b1.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(report_path)
    if tests.returncode:
        raise SystemExit(tests.returncode)
    print(f'PASS: {len(original_before)} original files unchanged; {len(products_after)} outputs deterministic.')


if __name__ == '__main__':
    main()
