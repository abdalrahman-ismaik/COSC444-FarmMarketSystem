"""Package the final LaTeX report and only its used figure assets."""
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/report/latex'
PDF = ROOT / 'submission/FarmMarketSystem_B1_Technical_Report.pdf'
OUT = ROOT / 'submission/FarmMarketSystem_B1_Technical_Report_Source.zip'


def main():
    tex = SOURCE / 'farm-to-market-report.tex'
    assets = set(re.findall(r'\{(figures/[^}]+\.(?:png|pdf))\}', tex.read_text(encoding='utf-8')))
    names = sorted(assets | {'farm-to-market-report.tex', 'README.md', 'figures/gui/sources.json'})
    payload = {name: (SOURCE / name).read_bytes() for name in names}
    payload[PDF.name] = PDF.read_bytes()
    with zipfile.ZipFile(OUT, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(OUT) as archive:
        assert archive.testzip() is None, 'Archive CRC failed'
        assert set(archive.namelist()) == set(payload), 'Archive members differ'
        for name, data in payload.items():
            assert archive.read(name) == data, f'Payload differs: {name}'
    print(f'{OUT.name}: {len(payload)} verified members, {len(assets)} figure assets')


if __name__ == '__main__':
    main()
