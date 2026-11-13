"""Isolated entry point: add only this repository's trusted scripts directory."""
from pathlib import Path
import os
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
if __name__ == '__main__':
    scratch=Path(__file__).resolve().parents[1]/'build/tmp'
    scratch.mkdir(parents=True,exist_ok=True)
    os.environ['TMPDIR']=str(scratch)
    tempfile.tempdir=str(scratch)
    import importlib
    action = sys.argv.pop(1)
    if action not in {'prepare', 'inventory', 'build', 'gate', 'render', 'checks', 'icon_measure', 'verify'}:
        raise SystemExit('Unknown action')
    importlib.import_module(action).main()
