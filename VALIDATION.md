# Implementation and verification

Verified on this Mac on 2026-11-12. Local main only; no remote or push. This is an upright baseline workshop, not a release-quality font approval.

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

Opened and visually inspected the final serif waterfall/paragraphs, weather numerals, mono ligatures on/off and terminal, glass-over-map mockup, glyph points and icon grid. They show real text and actual geometry. FontFace load checks, cmap coverage, computed-family checks and HarfBuzz fingerprints all pass. At 32 px, measured Sans/Serif/Mono widths were 427.234375 / 409.968201 / 511.999969 px; matching expected widths were 427.234375 / 410.016 / 512 px (maximum difference under 0.048 px). Missing specimen glyphs or mismatched fingerprints fail loudly.

Chromium renders candidate and pinned unmodified open-font controls. Its system serif/mono generics fall back on this Mac, so those extra sheets are not emitted. WebKit renders installed system families, including ui-serif; its serif/mono widths differ from the generic fallback fingerprints. Apple font files were never opened, copied or parsed. Apple outline sheets are raster text zooms without point data.

**SF Symbols skipped:** all eight private-use probes produced the same missing-glyph fingerprint through system-ui in WebKit. No symbol app export, SVG, font file or stored outline was used. Hugeicons references use free-package SVG data only; no Pro package was accessed.

## External candidate test

A fresh candidate copied the three UFO/designspace trees and imported a hand-written SVG from an external directory with spaces in its path. `make build`, `make gate` and `make render` all accepted `ICONS_DIR` pointing to that directory. Its distinct stroke width 1.75 passed and 26 anonymous PNGs were rendered. Import/build/gate/render wall times: 14.179 / 9.134 / 40.413 / 23.26 seconds. This verifies the new-candidate font layout as well as external icon overrides. Test reports remain ignored under build; disposable candidate copies were removed after verification.

## Files

Created Makefile, uv/Python lock and version pin, npm/TypeScript lock, fetch/resource/source-conversion/build/gate/render/label/import/inventory/verification scripts, upstream.lock.json, license notices/RFN record, inventory/icons.json, baseline UFO/designspace trees, 272 semantic baseline SVGs, transform instructions, README.md, and this report. Generated fonts, TSX, optimized SVGs, raw gate evidence and HTML stay in ignored build/. Raw upstreams stay in ignored sources/upstream/. No Strata-Weather application files, dev server, cloud resources or remotes were changed.
