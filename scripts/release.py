"""Package a versioned release bundle under dist/ from a built candidate."""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, release_version, opentype_revision
from gate import checked_build


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_dist(cand: str, icon_set: str = 'r15-icons', icons_dir: str | None = None) -> dict:
    _, build_dir, report, _ = checked_build(cand, icons_dir)
    ver = release_version()
    _, rev_str = opentype_revision(ver)
    dist = ROOT / 'dist'
    shutil.rmtree(dist, ignore_errors=True)
    (dist / 'fonts' / 'core').mkdir(parents=True)
    (dist / 'fonts' / 'full').mkdir(parents=True)

    release = {
        'version': ver,
        'opentypeRevision': rev_str,
        'typeCandidate': cand,
        'iconSet': icon_set,
        'fonts': {},
        'icons': {},
    }
    for face, info in report['faces'].items():
        ttf_name = info['ttf']
        woff_name = info['woff2']
        shutil.copyfile(build_dir / ttf_name, dist / 'fonts' / 'core' / ttf_name)
        shutil.copyfile(build_dir / woff_name, dist / 'fonts' / 'core' / woff_name)
        full_ttf = ROOT / info['full_ttf']
        full_woff_out = dist / 'fonts' / 'full' / woff_name
        ft = TTFont(full_ttf, recalcTimestamp=False)
        ft['head'].created = ft['head'].modified = 3406620153
        ft.flavor = 'woff2'
        ft.save(full_woff_out)
        release['fonts'][face] = {
            'coreWoff2': f'fonts/core/{woff_name}',
            'coreWoff2Bytes': (dist / 'fonts' / 'core' / woff_name).stat().st_size,
            'coreWoff2Sha256': sha256_file(dist / 'fonts' / 'core' / woff_name),
            'coreTtf': f'fonts/core/{ttf_name}',
            'coreTtfBytes': (dist / 'fonts' / 'core' / ttf_name).stat().st_size,
            'coreTtfSha256': sha256_file(dist / 'fonts' / 'core' / ttf_name),
            'fullWoff2': f'fonts/full/{woff_name}',
            'fullWoff2Bytes': full_woff_out.stat().st_size,
            'fullWoff2Sha256': sha256_file(full_woff_out),
        }

    shutil.copytree(build_dir / 'icons', dist / 'icons')
    (dist / 'icons' / 'typecheck.log').unlink(missing_ok=True)
    shutil.copytree(build_dir / 'licenses', dist / 'licenses')

    manifest = json.loads((dist / 'icons' / 'manifest.json').read_text())
    release['icons'] = {
        'count': len(manifest['icons']),
        'strokeWidth': manifest['stroke_width'],
        'woff2': 'icons/StrataIcons.woff2',
        'woff2Bytes': (dist / 'icons' / 'StrataIcons.woff2').stat().st_size,
        'woff2Sha256': sha256_file(dist / 'icons' / 'StrataIcons.woff2'),
        'manifest': 'icons/manifest.json',
    }
    (dist / 'release.json').write_text(json.dumps(release, indent=2) + '\n')
    print(f'dist packaged: version {ver} ({cand} + {icon_set})', flush=True)
    return release


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cand', default='r12-type')
    p.add_argument('--icon-set', default='r15-icons')
    p.add_argument('--icons-dir')
    args = p.parse_args()
    package_dist(args.cand, args.icon_set, args.icons_dir)


if __name__ == '__main__':
    main()
