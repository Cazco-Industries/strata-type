"""Fetch locked data only. Never execute code from an upstream checkout."""
import base64
import hashlib
import json
import pathlib
import shutil
import subprocess
import tarfile
import tempfile
import sys
import zipfile
import io

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'sources/upstream'


def space():
    free = shutil.disk_usage('/').free
    if free < 16 * 1024**3:
        raise SystemExit('Fetch requires 16 GiB free, preserving the 14 GiB floor')


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', *args], text=True).strip()


def main():
    lock = json.loads((ROOT / 'upstream.lock.json').read_text())
    DEST.mkdir(parents=True, exist_ok=True)
    for entry in lock['git']:
        space()
        path = DEST / entry['id']
        if not path.exists():
            path.mkdir()
            git('init', '-q', str(path))
            git('-C', str(path), 'fetch', '--depth=1', '--filter=blob:none', entry['url'], entry['sha'])
            if entry.get('sparse'):
                git('-C', str(path), 'sparse-checkout', 'init', '--no-cone')
                git('-C', str(path), 'sparse-checkout', 'set', '--no-cone', *entry['sparse'])
            git('-C', str(path), 'checkout', '--detach', '-q', 'FETCH_HEAD')
        if entry.get('sparse'):
            git('-C', str(path), 'sparse-checkout', 'set', '--no-cone', *entry['sparse'])
        actual = git('-C', str(path), 'rev-parse', 'HEAD')
        if actual != entry['sha'] or git('-C', str(path), 'status', '--porcelain'):
            raise SystemExit(f'Upstream checkout changed: {path}')
        if git('-C', str(path), 'rev-parse', '--is-shallow-repository') != 'true':
            raise SystemExit(f'Non-shallow checkout rejected: {path}')
        print(f"{entry['id']}: {actual}", flush=True)
    for entry in lock['npm']:
        space()
        path = DEST / entry['id']
        marker = path / '.integrity'
        if marker.exists() and marker.read_text() == entry['integrity']:
            continue
        data = subprocess.check_output(['curl', '--fail', '--silent', '--show-error', '--location', '--max-time', '120', entry['url']])
        expected = entry['integrity'].removeprefix('sha512-')
        if base64.b64encode(hashlib.sha512(data).digest()).decode() != expected:
            raise SystemExit('Package integrity mismatch')
        with tempfile.TemporaryDirectory(dir=DEST) as temp:
            archive = pathlib.Path(temp) / 'package.tgz'
            archive.write_bytes(data)
            with tarfile.open(archive) as tar:
                # Python's data filter rejects traversal, device nodes, unsafe links.
                tar.extractall(pathlib.Path(temp) / 'unpacked', filter='data')
            shutil.rmtree(path, ignore_errors=True)
            shutil.move(str(pathlib.Path(temp) / 'unpacked/package'), path)
        marker.write_text(entry['integrity'])
        print(f"{entry['id']}: {entry['version']} (integrity verified)", flush=True)
    for entry in lock.get('artifacts', []):
        space()
        path = DEST / entry['id']
        target = path / entry['target']
        if target.exists():
            continue
        data = subprocess.check_output(['curl', '--fail', '--silent', '--show-error', '--location', '--max-time', '120', entry['url']])
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise SystemExit('Release archive checksum mismatch')
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            content = archive.read(entry['member'])
        path.mkdir(exist_ok=True)
        target.write_bytes(content)
        print(f"{entry['id']}: {entry['version']} (checksum verified)", flush=True)
    sys.path.insert(0, str(ROOT / 'scripts'))
    from free_icons import convert_package
    count = convert_package(DEST / 'hugeicons-free', DEST / 'hugeicons-free-svg')
    print(f'Free stroke-rounded SVGs: {count}', flush=True)
    # Copy only notices, not font binaries, into the tracked license directory.
    for entry in lock['git'] + lock['npm']:
        path = DEST / entry['id']
        notices = [p for p in path.iterdir() if p.is_file() and (p.name.lower().startswith('license') or p.name.lower() in ('ofl.txt', 'ofl.md'))]
        if not notices:
            raise SystemExit(f"No root license found for {entry['id']}")
        for notice in notices:
            shutil.copyfile(notice, ROOT / 'licenses' / f"{entry['id']}-{notice.name}")


if __name__ == '__main__':
    main()
