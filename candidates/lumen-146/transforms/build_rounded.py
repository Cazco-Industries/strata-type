"""Compatibility entry point; the standard builder now includes Rounded."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from build import build

if __name__=='__main__':
    candidate=Path(__file__).resolve().parents[1]
    build(candidate.name,'core',candidate/'review-icons')
