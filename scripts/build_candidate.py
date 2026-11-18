"""Build and self-check a clean, review-only course project ZIP."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission'
ZIP_PATH = OUT / 'FarmMarketSystem_B1_review_candidate.zip'
MANIFEST_PATH = OUT / 'MANIFEST.md'
ALLOW_FILES = {
    'README.md', 'PRODUCT.md', 'DESIGN.md', 'PROGRESS.md',
    'setup.bat', 'run.bat', '.gitignore',
    'submission/README.md', 'submission/technical-report.pdf', 'submission/poster.pdf',
    'submission/.gitattributes',
    'scripts/build_candidate.py',
}
ALLOW_DIRS = ('app', 'docs')
EXCLUDED_PARTS = {'.git', '.local', '.venv', 'venv', '__pycache__', '.pytest_cache',
                  '.mypy_cache', '.ruff_cache', 'archive', '.agents', 'skills', 'output'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo', '.log', '.zip'}
STAMP = (2026, 11, 17, 0, 0, 0)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example'):
        return False
    return True


def files_to_package() -> list[Path]:
    files = [ROOT / name for name in ALLOW_FILES if (ROOT / name).is_file()]
    for directory in ALLOW_DIRS:
        base = ROOT / directory
        files.extend(p for p in base.rglob('*') if p.is_file() and included(p))
    files = sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())
    if not files:
        raise RuntimeError('Package input list is empty')
    return files


def member_manifest(payloads: dict[str, bytes]) -> str:
    rows = ['# Review-candidate ZIP manifest', '',
            'This archive is for team review; it is not an accepted or submitted course package.',
            'SHA-256 covers each payload member listed below. The embedded manifest cannot hash itself,',
            'and the archive hash is recorded only in the external `submission/MANIFEST.md`.', '',
            '| ZIP member | Bytes | SHA-256 |', '|---|---:|---|']
    rows.extend(f'| `{name}` | {len(data)} | `{sha(data)}` |'
                for name, data in sorted(payloads.items()))
    rows += ['', 'Excluded: Git metadata, real `.env` files, local virtual environments, `.local`,',
             'generated output/logs/caches, archived ZIPs, and agent skill folders.']
    return '\n'.join(rows) + '\n'


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = files_to_package()
    payloads = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in paths}
    forbidden = [name for name in payloads if any(part in EXCLUDED_PARTS for part in PurePosixPath(name).parts)]
    if forbidden:
        raise RuntimeError(f'Excluded path entered package: {forbidden}')
    if any(name.endswith('/.env') or name == '.env' for name in payloads):
        raise RuntimeError('Real .env file entered package')
    readme = payloads.get('README.md', b'').decode('utf-8')
    for needed in ('setup.bat', 'run.bat', 'docs/PROJECT_REQUIREMENTS.md',
                   'docs/RUBRIC_AND_COVERAGE.md', 'docs/BUILD_DOCUMENTS.md'):
        if needed not in payloads and needed not in readme:
            raise RuntimeError(f'Required setup/document reference missing: {needed}')
    embedded = member_manifest(payloads).encode('utf-8')
    all_members = dict(payloads)
    all_members['MANIFEST.md'] = embedded
    temp_zip = ZIP_PATH.with_suffix('.building.zip')
    with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, data in sorted(all_members.items()):
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)
    archive_bytes = temp_zip.read_bytes()
    temp_zip.replace(ZIP_PATH)
    external = member_manifest(payloads)
    embedded_hash_row = f'| `MANIFEST.md` | {len(embedded)} | `{sha(embedded)}` |\n'
    external = external.replace('\nExcluded:', '\n' + embedded_hash_row + '\nExcluded:', 1)
    external += f'\nZIP SHA-256: `{sha(archive_bytes)}`\nZIP bytes: {len(archive_bytes)}\n'
    MANIFEST_PATH.write_text(external, encoding='utf-8', newline='\n')

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-dir', type=Path, help='new empty directory for ZIP extraction/hash checks')
    args = parser.parse_args()
    extract = args.verify_dir or (ROOT / '.local' / 'candidate-extraction-20261117')
    if not extract.is_absolute():
        extract = ROOT / extract
    extract = extract.resolve()
    local_root = (ROOT / '.local').resolve()
    if local_root not in extract.parents:
        raise RuntimeError('Verification directory must be inside this repo .local folder')
    if extract.exists():
        raise RuntimeError(f'Preserving existing extraction; choose a new --verify-dir: {extract}')
    extract.mkdir(parents=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError('Duplicate ZIP member names')
        for info in zf.infolist():
            rel = PurePosixPath(info.filename)
            if rel.is_absolute() or '..' in rel.parts:
                raise RuntimeError(f'Unsafe ZIP member path: {info.filename}')
            target = extract.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info.filename))
    for name, data in payloads.items():
        actual = (extract / Path(*PurePosixPath(name).parts)).read_bytes()
        if sha(actual) != sha(data):
            raise RuntimeError(f'Extracted member hash mismatch: {name}')
    inner_bytes = (extract / 'MANIFEST.md').read_bytes()
    inner = inner_bytes.decode('utf-8')
    if sha(inner_bytes) != sha(embedded):
        raise RuntimeError('Embedded manifest hash mismatch')
    if 'not an accepted or submitted' not in inner:
        raise RuntimeError('Review-only notice missing from embedded manifest')
    for required in ('README.md', 'setup.bat', 'run.bat', 'app/.env.example',
                     'app/schema.sql', 'app/app.py', 'docs/report/technical-report.md',
                     'docs/report/build_documents.py', 'docs/poster/poster.json',
                     'docs/diagrams/conceptual-er.drawio', 'docs/diagrams/relational-schema.drawio'):
        if not (extract / Path(*PurePosixPath(required).parts)).is_file():
            raise RuntimeError(f'Fresh extraction missing required path: {required}')
    if ZIP_PATH.name in names or any('original-package' in name.lower() for name in names):
        raise RuntimeError('Archive contains itself or an original package archive')
    print(json.dumps({'zip': str(ZIP_PATH), 'bytes': len(archive_bytes),
                      'archive_sha256': sha(archive_bytes), 'members': len(all_members),
                      'extracted_to': str(extract), 'required_paths': 'pass',
                      'member_hashes': 'pass', 'excluded_path_check': 'pass'}, indent=2))


if __name__ == '__main__':
    main()
