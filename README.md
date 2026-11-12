# Strata type

Local font and icon workshop. No remotes, uploads, app integration, Apple font
files, or proprietary icon packages are needed. Forks are OFL 1.1; SVG/React/icon
font output bundles the ISC/MIT notices. Read [DESIGN-BRIEF.md](DESIGN-BRIEF.md)
and [licenses/RFN.md](licenses/RFN.md) before editing.

```sh
uv sync --frozen
npm ci --ignore-scripts
.venv/bin/python -I -m playwright install chromium webkit
scripts/fetch_upstream.sh
make inventory                         # reads sibling strata-weather only
make prepare                           # once: Glyphs → UFO, native Serif UFOs
make build CAND=baseline SUBSET=core
make gate CAND=baseline
make render CAND=baseline REFS=1 \
  OUT="$HOME/strata-ml/type-climb/renders/test" \
  MAP="$HOME/strata-ml/type-climb-lead/labels.map"
make build CAND=baseline SUBSET=full
make verify
```

`uv.lock` pins the Python toolchain (Python 3.12); Python Playwright pins browser
revisions. `package-lock.json` pins the TypeScript parser/compiler and React
types. All Python entry points use `-I`; no upstream scripts, npm imports,
plugins, or app code execute. The five git checkouts are shallow and pinned;
the free icon package has SHA-512 integrity and the open font control archive
has SHA-256 integrity. Upstreams live in ignored `sources/upstream/`.

`candidates/<id>/fonts/{sans,serif,mono}/` each contain one `.designspace` and
its editable UFO masters. `icons/` contains semantic SVG names on a 24 grid.
`inventory/icons.json` records the read-only app scan, mappings, approximations,
and library gaps. Baseline icon geometry comes from Lucide; it does not claim
that reused shapes constitute the finished weather library. Baselines are
upright only. Rounding, metrics harmonization, extra scripts, and new glyphs
are design work for later.

To iterate, copy `candidates/baseline` to `candidates/<id>`, put your deterministic
ufoLib2/fontTools edits in `<id>/transforms/`, run them explicitly with the
isolated interpreter, then build → gate → render. Transforms never execute
implicitly. Or import a builder directory:

```sh
.venv/bin/python -I scripts/import_candidate.py --id round-one --icons /path/to/svg
# Optional --fonts /path/to/fonts, with the same three-face directory layout.
make build CAND=round-one ICONS_DIR=/path/to/svg
make gate CAND=round-one ICONS_DIR=/path/to/svg
make render CAND=round-one ICONS_DIR=/path/to/svg OUT=/empty/reviewer/dir MAP=/lead/map.json
```

`ICONS_DIR` overrides only icons, for all three commands; it is read-only. Use
the same input for build/gate/render. Changed source or binary bytes fail stale
build checks. Whole source bytes and locked tooling determine compile caches;
core output retains all layout features and their substitution closure. Full
builds compile every exported glyph; core output is a Unicode subset of that
same variable font. Both ship TTF and WOFF2. SVGs are XML-minified; strokes are
expanded into filled contours for the icon WOFF2. Its codepoint manifest is
per-build; use semantic React exports when stable identities are needed.

Gates write `build/<id>/gate.{json,md}` and raw Fontbakery/interpolation reports.
The universal profile runs with network checks explicitly skipped. Name-table,
SVG and generated TSX violations fail immediately. Baseline coverage,
interpolation and Fontbakery quality failures remain visible in `quality_status`;
report generation succeeds so a baseline can be reviewed. Add `--strict` to
`scripts/run.py gate` to reject every quality failure. No missing glyph is
silently supplied from a different face. Metrics are measured, not harmonized.

Rendering needs an **empty OUT** and a **lead-only JSON MAP outside OUT**.
`newlabel.py --key <identity> --map /lead/map.json` mints opaque labels; the
renderer adds missing labels automatically. OUT contains PNGs plus an anonymous
index only. HTML, fallback checks, engine comparisons and skipped-reference
reasons stay under `build/<id>/`. Chromium renders the candidate and the three
unmodified open-font controls. WebKit renders installed system families; a
Chromium comparison is emitted if system widths differ and every requested system family resolves without fallback. Apple glyph zooms are
raster text only, never outline diagrams. SF Symbols are emitted only when
WebKit's system-font PUA probes distinguish them from missing-glyph boxes.
Every final PNG is decoded after stripping metadata; a lossless IDAT reframing
also removes accidental identity words from compressed bytes, so literal grep
of OUT is clean. `python -I scripts/blindcheck.py OUT` repeats the audit.

CPU work pauses in UTC :00–:05, :15–:20, :30–:35 and :45–:50 windows, on the
shared pause flag. Memory pressure ≥2 pauses between bounded units after data collection, so an interrupted allocation does not hold the machine under pressure. The guard checks disk continuously,
pausing below a 15 GiB reserve to preserve the 14 GiB floor. Do not disable it.
Build timings exclude setup and report guard pauses separately. Intermediate
masters are deleted by fontmake; content-addressed full TTFs are the iteration
cache. Remove old `build/.cache/` entries when no longer needed.
