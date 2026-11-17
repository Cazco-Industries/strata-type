"""Rebuild this candidate's sources from the baseline, deterministically.

Run from the repository root:
    .venv/bin/python -I candidates/r10-type/transforms/apply.py [faces...]

Faces default to: sans rounded serif mono. Each face folder is reset from
candidates/baseline/fonts before its transforms run, so the result depends
only on the baseline bytes and these scripts.
"""
import shutil
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
CAND = HERE.parent
ROOT = CAND.parents[1]
BASE = ROOT / 'candidates' / 'baseline' / 'fonts'
FONTS = CAND / 'fonts'
REF_DIR = None
TEMP_MODE = None

import ufoLib2  # noqa: E402
import hygiene  # noqa: E402
import tangency  # noqa: E402


def load(face, prefix, count):
    return {f'm{i:02d}': ufoLib2.Font.open(FONTS / face / f'{prefix}-m{i:02d}.ufo') for i in range(count)}


def save(face, prefix, masters):
    for m, f in masters.items():
        f.save(FONTS / face / f'{prefix}-{m}.ufo', overwrite=True)


def reset(face):
    shutil.rmtree(FONTS / face, ignore_errors=True)
    shutil.copytree(BASE / face, FONTS / face)


def main(faces):
    if 'sans' in faces:
        import sans
        reset('sans')
        hygiene.sans(FONTS / 'sans')
        ms = load('sans', 'StrataSans', 6)
        sans.run(ms)
        print('sans tangent joins restored (points, glyphs)', tangency.restore(ms, BASE / 'sans', 'StrataSans'))
        save('sans', 'StrataSans', ms)
        sans.weight_map(FONTS / 'sans')
        print('sans caption stems', sans.caption(FONTS / 'sans'))
        print('sans done', flush=True)
    if 'rounded' in faces:
        import rounded
        rounded.make(FONTS / 'sans')
        print('rounded done', flush=True)
    if 'serif' in faces:
        import serif

        def serif_pass():
            reset('serif')
            hygiene.serif(FONTS / 'serif')
            ms = load('serif', 'StrataSerif', 9)
            serif.run(ms, FONTS / 'serif')
            print('serif tangent joins restored (points, glyphs)', tangency.restore(ms, BASE / 'serif', 'StrataSerif', relead=True, keep=serif.KEEP_DRAWN))
            print('serif short pieces spread (before, after)', serif.spread_short(ms))
            return ms

        # The reference pass runs the same steps with r6's caption settings;
        # its quadratic splits are the ones every segment keeps (see
        # serif.keep_splits).
        with serif.caption_profile(serif.R6_CAPTION):
            ref = serif_pass()
        if REF_DIR:
            REF_DIR.mkdir(parents=True, exist_ok=True)
            for m, f in ref.items():
                f.save(REF_DIR / f'StrataSerif-{m}.ufo', overwrite=True)
        splits = serif.split_counts(ref)
        del ref
        print('serif reference pass done', flush=True)
        ms = serif_pass()
        pinned, left, travel = serif.keep_splits(ms, splits)
        print('serif quadratic splits kept at the reference (glyphs, segments)', pinned, flush=True)
        print('serif largest handle travel (units, glyph, segment, masters)', travel[:10], flush=True)
        save('serif', 'StrataSerif', ms)
        if left:
            sys.exit(f'serif quadratic splits differ from the reference in {left}')
        print('serif done', flush=True)
    if 'mono' in faces:
        import mono
        if TEMP_MODE:
            mono.TEMP_MODE = TEMP_MODE
        reset('mono')
        ms = load('mono', 'StrataMono', 2)
        ms = mono.run(ms, FONTS / 'mono')
        print('mono tangent joins restored (points, glyphs)', tangency.restore(ms, BASE / 'mono', 'StrataMono'))
        save('mono', 'StrataMono', ms)
        print('mono done', flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('faces',nargs='*')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--dump-ref',type=Path,help='also save the serif reference masters here')
    parser.add_argument('--temp-mode',help='mono degree-letter construction to build (default: mono.TEMP_MODE)')
    args=parser.parse_args()
    REF_DIR=args.dump_ref.resolve() if args.dump_ref else None
    TEMP_MODE=args.temp_mode
    if not set(args.faces)<={'sans','rounded','serif','mono'}:parser.error('Unknown face')
    if args.output_dir:
        FONTS=args.output_dir.resolve()/'fonts'
        FONTS.mkdir(parents=True,exist_ok=True)
    main(args.faces or ['sans', 'rounded', 'serif', 'mono'])
