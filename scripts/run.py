"""Isolated entry point: add only this repository's trusted scripts directory."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
if __name__ == '__main__':
    import importlib
    action = sys.argv.pop(1)
    if action not in {'prepare', 'inventory', 'build', 'gate', 'render', 'verify'}:
        raise SystemExit('Unknown action')
    importlib.import_module(action).main()
