# Implementation and verification

Verified on this Mac on 2026-11-12. Local main only; no remote or push. This is an upright baseline workshop, not a release-quality font approval.

The initial workshop measurements below are historical. Their wrapper-only
font check missed the browser's `pre` font override, and they did not establish
surface contrast or headline line contact. The specimen harness repair record
below supersedes those render claims. Original round-0 review files are retained.

## Commands and timings

| Command | Wall time | Result |
| --- | ---: | --- |
| `scripts/fetch_upstream.sh` | 3.14 s | PASS; cached pinned checkouts/package; converted all 6,100 free stroke-rounded SVGs |
| `make build CAND=baseline SUBSET=core` | 43.47 s | PASS; cold compile cache, all three faces plus 272 icons |
| `make gate CAND=baseline` | 42.45 s | Report completed; zero hard failures, quality FAIL |
| `make render CAND=baseline OUT="$HOME/strata-ml/type-climb/renders/test" REFS=1 MAP="$HOME/strata-ml/type-climb-lead/labels.map"` | 68.70 s | PASS; 106 final PNGs at 2x |
| `make build CAND=baseline SUBSET=full` | 11.16 s | PASS; reuses the verified full compile cache |
| `make build CAND=baseline SUBSET=core` (restore) | 12.16 s | PASS; TTF/WOFF2 bytes identical to the gated core build |
| `make verify` | 1.01 s unpaused | 7 tests PASS; latest wall time 71.21 s included waiting for pressure to clear |

Core face timings were Sans 12.360 s, Serif 27.251 s, Mono 3.127 s. Full output timings were 5.156 / 3.802 / 1.360 s. The core command compiles complete variable fonts and then subsets them, retaining all OpenType feature closure. Full output is therefore a real full build through the same compiler, served from its content-addressed cache on that second invocation.

Guard waits were significant on earlier attempts: macOS repeatedly reported pressure level 2. The successful cold core run above had no guard wait. CPU work stops during the protected UTC windows. Memory pressure waits occur between bounded units after garbage collection, rather than suspending the allocation responsible for pressure. Root free space was approximately 33 GiB initially and never observed below 28 GiB during this task.

## Gate summary

| Face | Pass | Warn | Fail | Error | Core coverage | Master interpolation | Core WOFF2 |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Strata Sans | 91 | 4 | 6 | 1 | 257/258 | none | 92,920 B |
| Strata Serif | 94 | 5 | 6 | 0 | 240/258 | {'kink': 5} | 189,472 B |
| Strata Mono | 88 | 7 | 6 | 1 | 237/258 | {'contour_order': 5} | 44,792 B |

The universal profile was run completely with network checks explicitly skipped. Raw results include INFO and SKIP counts. `fontTools.varLib.interpolatable` was run on every full source designspace. Fontbakery also examines compiled interpolation, so its findings can differ from the source-master check.

All three name-table RFN gates pass. Every SVG passes the 24 viewBox, stroke-only, consistent width 2, round cap/join, no-transform contract; all generated TSX typechecks. The 272-glyph icon WOFF2 is 16,416 bytes. Strokes are expanded to closed, filled contours for font use.

Quality FAIL is deliberate and visible: no upstream contour, metrics, caret, hinting or coverage findings were redesigned away. There are also compilation metadata limitations, not merely upstream outline warnings: Sans/Mono have a STAT table without AxisValueArray and Fontbakery 1.1 raises one ERROR per face while inspecting it; Sans has repeated text/display instance labels; Serif retains native Text 1 default-style and version metadata inconsistencies, plus long STAT style combinations. These remain recorded, not waived or described as passes. The report command returns success when reporting these baseline findings; RFN, SVG and TSX hard failures return nonzero. `--strict` rejects all quality failures.

## Normalized metrics

Values are em fractions at each variable font default. hhea / typo / win ascender and descender magnitudes happen to match within each baseline; they have not been harmonized across faces. All hhea and typo line gaps are zero. Win descenders below are shown as positive magnitudes.

| Face | UPM | x-height | Cap | hhea asc/desc | Typo asc/desc | Win asc/desc | wght min/default/max | opsz min/default/max |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| Strata Sans | 2048 | 0.5459 | 0.72754 | 0.96875/-0.24121 | 0.96875/-0.24121 | 0.96875/0.24121 | [100.0, 400.0, 900.0] | [14.0, 14.0, 32.0] |
| Strata Serif | 1000 | 0.475 | 0.67 | 1.036/-0.335 | 1.036/-0.335 | 1.036/0.335 | [200.0, 400.0, 900.0] | [8.0, 20.0, 60.0] |
| Strata Mono | 1950 | 0.53846 | 0.70462 | 0.92308/-0.30769 | 0.92308/-0.30769 | 0.92308/0.30769 | [300.0, 300.0, 700.0] | none |

**Strata Sans figures, 0–9:**

- tnum: `[0.64844, 0.64844, 0.64844, 0.64844, 0.64844, 0.64844, 0.64844, 0.64844, 0.64844, 0.64844]`
- pnum: `[0.63086, 0.40674, 0.60986, 0.61768, 0.646, 0.59326, 0.62012, 0.55176, 0.61865, 0.62012]`
- Missing core codepoints: `U+00AD`

**Strata Serif figures, 0–9:**

- tnum: `[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]`
- pnum: `[0.502, 0.426, 0.508, 0.503, 0.497, 0.497, 0.488, 0.454, 0.509, 0.52]`
- Missing core codepoints: `U+2000, U+2001, U+2008, U+2011, U+201B, U+2103, U+2109, U+2150, U+2151, U+2152, U+2155, U+2156, U+2157, U+2158, U+2159, U+215A, U+2194, U+2195`

**Strata Mono figures, 0–9:**

- tnum: `[0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538]`
- pnum: `[0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538, 0.61538]`
- Missing core codepoints: `U+2000, U+2001, U+2002, U+2003, U+2004, U+2005, U+2006, U+2009, U+200A, U+2010, U+2011, U+201B, U+202F, U+2032, U+2033, U+2071, U+2103, U+2109, U+2150, U+2151, U+2152`

Sans and Serif have distinct proportional/tabular figures. Mono keeps its upstream fixed advances and has no pnum feature. Serif and Mono both lack dedicated ℃/℉ glyphs; those are reported as missing rather than supplied by fallback or newly drawn in this task. The exact 258-codepoint core set is defined in `scripts/common.py`.

## Inventory and licenses

`inventory/icons.json` records 182 Lucide import names, 604 imports, 742 static identifier occurrences, 25 condition glyphs, 36 NWS codes in each day/night map, 49 statically referenced Erik Flowers IDs, and 50 distinct library gaps. The full 219-icon gallery catalog is listed separately from actual resolver/UI references. TypeScript AST counts are occurrences, not runtime render counts. No subpath Lucide import path was found in apps/packages.

The final semantic aliases distinguish night partly-cloudy from overcast and do not infer gusts from “windy”. Regenerating all baseline icon SVGs and their manifest after those inventory corrections produced identical source bytes. Baseline weather shapes are explicitly marked approximations; their presence does not claim the complete weather library is designed.

Pins: Inter v4.1 e3a3d4c57d5ecc01453a575621882a384c1995a3; Source Serif native sources 4.005 17cfec64bc132c81255dda15ea64a0bf27ef4da9, release control 4.005R 2823e993c53fca27c5c8749f529b56a5a7c77b6b; Fira Code 6.2 eee6db993696aba61ff4eef03698e2987d79910c; Lucide 0.468.0 f12b0de177fbc2a6795e99be065887e72b237123; Hugeicons core-free-icons 4.4.0 with locked SHA-512 integrity. The Fira open-font control archive is SHA-256 pinned. All git checkouts are shallow.

Each OFL was read. Source explicitly reserves “Source”. The pinned Inter and Fira notices declare no RFN; the brief’s stricter rule still blocks Inter, Source and Fira in every binary name record. Original copyright lines are retained verbatim in bundled notices and candidate COPYRIGHT.txt files. To reconcile that with the ban on those words in every name record, binary name ID 0 points to the bundled notices. See `licenses/RFN.md` for the exact policy. Font forks remain OFL 1.1; icon output bundles ISC/MIT notices.

## Render verification and limits

Final review directory: `~/strata-ml/type-climb/renders/test/`. Lead map: `~/strata-ml/type-climb-lead/labels.map` (outside review output). No reverse mapping appears in OUT. HTML, font probes and engine evidence stay in `build/baseline/`. PNGs carry no text/exif metadata; lossless IDAT reframing also handles Unicode case folding in grep. The literal command below exited 1 with no matches:

```sh
rg -a -i -l 'Strata|Inter|Source|Fira|SF|New[ _-]?York|Lucide|Hugeicons|baseline|reference' "$HOME/strata-ml/type-climb/renders/test"
```

Opened and visually inspected the initial serif waterfall/paragraphs, weather numerals, mono ligatures on/off and terminal, glass-over-map mockup, glyph points and icon grid. FontFace load checks, cmap coverage, wrapper-family checks and HarfBuzz fingerprints passed, but did not prove the face used by descendant `pre` elements. At 32 px, measured Sans/Serif/Mono probe widths were 427.234375 / 409.968201 / 511.999969 px; matching expected widths were 427.234375 / 410.016 / 512 px (maximum difference under 0.048 px). The repaired checks inspect actual text descendants and are recorded below.

The initial run rendered candidates and pinned unmodified open-font controls. The repair removes the duplicate open-font label, retaining baseline as the single such control. Chromium's system serif/mono generics fall back on this Mac, so those extra sheets are not emitted. WebKit renders installed system families, including ui-serif; its serif/mono widths differ from the generic fallback fingerprints. Apple font files were never opened, copied or parsed. Apple outline sheets are raster text zooms without point data.

**SF Symbols skipped:** all eight private-use probes produced the same missing-glyph fingerprint through system-ui in WebKit. No symbol app export, SVG, font file or stored outline was used. Hugeicons references use free-package SVG data only; no Pro package was accessed.

## External candidate test

A fresh candidate copied the three UFO/designspace trees and imported a hand-written SVG from an external directory with spaces in its path. `make build`, `make gate` and `make render` all accepted `ICONS_DIR` pointing to that directory. Its distinct stroke width 1.75 passed and 26 anonymous PNGs were rendered. Import/build/gate/render wall times: 14.179 / 9.134 / 40.413 / 23.26 seconds. This verifies the new-candidate font layout as well as external icon overrides. Test reports remain ignored under build; disposable candidate copies were removed after verification.

## Files

Created Makefile, uv/Python lock and version pin, npm/TypeScript lock, fetch/resource/source-conversion/build/gate/render/label/import/inventory/verification scripts, upstream.lock.json, license notices/RFN record, inventory/icons.json, baseline UFO/designspace trees, 272 semantic baseline SVGs, transform instructions, README.md, and this report. Generated fonts, TSX, optimized SVGs, raw gate evidence and HTML stay in ignored build/. Raw upstreams stay in ignored sources/upstream/. No Strata-Weather application files, dev server, cloud resources or remotes were changed.

## Specimen harness repair (2026-11-12)

Fresh reviewer artifacts: `/tmp/type-harness-u9uocgcu/review/SHEETS.md`,
`review/renders/index.json`, and `review/renders/findings.json` under that same
scratch root. There are 145 PNGs: 41 for the control, 35 for each submitted
profile, and 34 retained system/numeric/free-icon control sheets. The fresh
lead-only map has no `ref:open` key; no duplicate open-font sheets are emitted.
The guide includes a visible per-surface line-contact table and links the raw
anonymous findings. These `/tmp` artifacts should be retained by the lead if
needed beyond this local handoff.

All commands ran locally, with the existing resource guard enabled. No candidate rebuild,
source-outline change, icon-directory change, dev-server operation, remote,
commit, push, upload, or production operation was performed. The pre-existing
`pre{font-family:inherit}` edit was preserved. Before/after SHA-256 comparison
passed for all 129,226 protected files, including all candidates, all existing
build icon directories, the two external icon sets, and the complete round-0
review directory. Evidence: `lead/protected-{before,check}.json` in scratch.
Root free space was checked with `df -h /` before each render/replay: 19–21 GiB
reported, above the 14 GiB floor. The first run paused for shared memory pressure
and the UTC :30–:35 window; the guard remained enabled throughout.

Reproduction commands (from the repository root):

```sh
make render CAND=baseline REFS=1 OUT=/tmp/type-harness-u9uocgcu/stage-a \
  MAP=/tmp/type-harness-u9uocgcu/lead/labels.map
make render CAND=lumen-146 \
  ICONS_DIR=/Users/rydercaswell/strata-ml/type-climb-work/lumen-146/icons \
  OUT=/tmp/type-harness-u9uocgcu/stage-b MAP=/tmp/type-harness-u9uocgcu/lead/labels.map
make render CAND=quartz-571 \
  ICONS_DIR=/Users/rydercaswell/strata-ml/type-climb-work/quartz-571/icons \
  OUT=/tmp/type-harness-u9uocgcu/stage-c MAP=/tmp/type-harness-u9uocgcu/lead/labels.map
make verify
.venv/bin/python -I scripts/review_set.py \
  --input /tmp/type-harness-u9uocgcu/stage-a \
  --input /tmp/type-harness-u9uocgcu/stage-b \
  --input /tmp/type-harness-u9uocgcu/stage-c \
  --out /tmp/type-harness-u9uocgcu/review/renders \
  --guide /tmp/type-harness-u9uocgcu/review/SHEETS.md
.venv/bin/python -I scripts/blindcheck.py /tmp/type-harness-u9uocgcu/review
.venv/bin/python -I scripts/blindcheck.py /tmp/type-harness-u9uocgcu/review/renders
```

OUT must be empty for a repeat; use a new directory and keep the same lead map.
Render wall times were 763.859 s including guard waits, 31.184 s, and 36.312 s.
Every render and the assembled guide/PNG/JSON set passed the blind audit. The
final focused suite passed all 14 tests in 2.371 s. The new browser regression
checks deliberately restore a generic `pre` override and a nested generic
reading-face override: both fail loudly. Deliberately low sky/terminal contrast
also fails. Separated headline lines are clear; compressed lines produce a
nonfatal finding. A tall component belonging to only one line is not reported
as a two-line collision.

A fresh replay of 36 representative sheets (all answer-card surfaces, all new
numeric comparisons, dark code sheets, icon-font sheets, first icon galleries,
and sky reading samples) produced identical decoded pixels. Recomputed
collision results were identical, including line boxes and component bounds.
This also verifies the added line-mask wrapping assertion on the earlier control
run. Replay evidence: `lead/replay.{py,json,log}` in scratch. Font/contrast reports
are retained in `build/<id>/render-audit.json` and copied to
`lead/audit-{a,b,c}.json`; these are outside the reviewer directory.

### Measured results

Every code sheet has seven `pre` elements. Each resolves to the intended `p2`
face, has a loaded FontFace and covered text, and measures its own first code
line against generic families. These are the smallest absolute width deltas
from `monospace` across the seven runs on both light/dark sheets (CSS pixels).

| Opaque label | Code family | Smallest mono width delta | Lowest sky contrast | Terminal contrast | Light / dark / glass headline contacts |
| --- | --- | ---: | ---: | ---: | --- |
| dawn-pearl-797 | p2 | 2.040024 px | 5.6573:1 | 14.9257:1 | clear / clear / clear |
| maple-dawn-749 | p2 | 3.373901 px | 5.6573:1 | 14.9257:1 | clear / clear / clear |
| fern-elm-968 | p2 | 2.038101 px | 5.6573:1 | 14.9257:1 | 1 / 1 / 1 joined component |

Contrast uses WCAG relative luminance, the computed foreground and ancestor
opacity, and the actual raster background beneath every text-run rectangle
with text hidden. It includes neutral captions. The lowest value across every
rendered sky sheet, including retained controls, is 5.6573:1 (required 4.5:1).
Every terminal measurement is 14.9257:1 (required 7:1).

Headline analysis uses 2× browser rasters and 8-connected components, with
black ink below grayscale 128. Each component must contain pixels from separate
per-line masks for adjacent DOM lines; overlapping font line boxes alone do not
qualify. Color-only masks are removed before the saved PNG. The real
`fern-elm-968` result joins lines 1 and 2: 1,958 ink pixels, CSS bounds
`[113.5, 252, 26.5, 80]` on light/dark and `[142.5, 292, 26.5, 80]` on glass.
It remains a reviewer-visible font result; no outline or headline spacing was
changed to hide it. The retained type-only control is clear on all three
answer-card surfaces.

### Repair evidence

Sheet paths below are relative to `/tmp/type-harness-u9uocgcu/review/renders/`.
The generated guide links all surfaces and labels.

| Defect | Implementation evidence | Fresh sheet evidence |
| --- | --- | --- |
| 1. Descendant font fallback | `scripts/render_audit.py:11`; called by `scripts/render.py:144`; explicit computed-family, loaded-face, cmap and generic-width checks | `dawn-pearl-797-19.png`, `maple-dawn-749-19.png`, `fern-elm-968-19.png` |
| 2. Icon/text fits | `scripts/specimens.py:105`; 13/15/17 px text crossed with 16/20 px own-set icons; 13 px tab labels; type-only omission | All three labels' `14`, `16`, `17` sheets; type-only `copper-jade-841-14.png` |
| 3. Semantic icon names and size caption | `scripts/specimens.py:163`, `scripts/specimens.py:172`; named SVG and font tiles, including free-icon control | `dawn-pearl-797-23.png`, `maple-dawn-749-35.png`, `fern-elm-968-32.png`, `jade-cobalt-864-01.png` |
| 4. Duplicate open-font control | `scripts/render.py:129`; fresh map has no duplicate key; control appears once in the guide | `dawn-pearl-797-01.png`; generated `SHEETS.md` and `index.json` |
| 5. Accurate icon-font title | `scripts/specimens.py:166`, `scripts/review_set.py:21` | `maple-dawn-749-35.png`, `fern-elm-968-35.png` |
| 6. Regular/Rounded comparison | `scripts/specimens.py:93`, `scripts/render.py:184`; matching five strings, regular above Rounded at 24/48/96 px | Both submitted labels' `25`, `28`, `31` sheets |
| 7. Sky contrast | `scripts/specimens.py:27`, `scripts/render_audit.py:76`; light gradient and opaque captions, measured hard gate | All three labels' `03` sheets; both submitted labels' `31` sheets |
| 8. Terminal contrast | `scripts/specimens.py:29`, `scripts/render_audit.py:103`; transparent inner pre over the dark panel | All three labels' `19` sheets |
| 9. Explicit units and meaning | `scripts/specimens.py:130`; “72°F” and “20% chance of rain” | All three labels' `14`, `16`, `17` sheets |
| 10. Nonfatal headline contacts | `scripts/render_audit.py:110`, `scripts/render.py:154`, `scripts/review_set.py:51` | `fern-elm-968-14.png`, `fern-elm-968-16.png`, `fern-elm-968-17.png`; `findings.json` |

Opened and visually inspected all three requested labels' light/dark/glass
answer cards, dark code/terminal sheets, sky reading samples, the two submitted
labels' regular/Rounded comparisons on all three surfaces, named icon grids and
icon-font tiles, the free-icon control, and the type-only answer card. The
contact at the first/second headline lines is visible in the flagged profile.
All final PNGs were reopened and decoded by the raster cleaner.

All ten harness defects are addressed. Existing font quality/coverage findings
remain unchanged. System symbol PUA probes still do not resolve reliably, so no
system-symbol sheet was emitted; reliable probes without verified semantic
names are also explicitly skipped rather than emitting unnamed tiles. These
local renders are specimen evidence, not font-release approval or app integration.
