# Rebuild the candidate

`design.py` reconstructs all font masters from `candidates/baseline/fonts` and
writes the numeric style to `fonts/sans-rounded/`. It accepts optional face
arguments and `--output-dir` to regenerate into an empty temporary directory.
It copies finished icons from `review-icons/` without modifying that input.
`build_rounded.py` is a compatibility entry point for the standard four-face
core build. Use the resource guard for both scripts. See `../DESIGN-NOTES.md`.
