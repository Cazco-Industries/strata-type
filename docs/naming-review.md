# Font & Icon Naming Review (`27.0.0.0`)

Audit of every name across the finalized **Strata** font family (`r12-type`) and icon library (`r15-icons`, 71 SVGs), verified directly against the compiled `27.0.0.0` binaries (`dist/fonts/core/*.ttf`, `dist/icons/StrataIcons.woff2`), designspace XMLs, FontBakery universal reports, `scripts/icons.py`, and the consumer contracts in `strata-weather`.

By owner decision for **`27.0.0.0`**:
- **All P0 OpenType binary metadata, versioning, and `STAT` bugs were fixed and verified** (zero outline or shaping drift; 0 FontBakery errors; 0 metadata/name/STAT/version failures).
- **All current font and icon names were kept as-is for `27.0.0.0`**, with P1/P2 alignment items tracked below for `strata-weather` integration or `27.1.0.0+`.

---

## Status Summary

| Priority | Status | Scope | Finding | Resolution / Next Action |
| --- | --- | --- | --- | --- |
| **P0** | **Resolved (`27.0.0.0`)** | `StrataSans.ttf` | 9 duplicate `fvar` Display instance names (`varfont/duplicate_instance_names` FAIL). | Fixed in `transforms/hygiene.py`: `opsz=32` instances now use `Display Thin`..`Display Black` (`Display` at 400) and `StrataSans-Display*`. 18/18 unique names. |
| **P0** | **Resolved (`27.0.0.0`)** | `StrataSerif.ttf` | Default instance named `"Text 1"` / `"StrataSerif-Text1"` (`valid_default_instance_nameids` FAIL). | Fixed in `transforms/hygiene.py` & `scripts/common.py`: default master & binary IDs 3/4/6/18 now report `Strata Serif Regular` / `StrataSerif-Regular`. |
| **P0** | **Resolved (`27.0.0.0`)** | `StrataSerif.ttf` | `Version 0.000` vs `head` `4.005` (`font_version` FAIL) and `STAT` `SmallText` >31 chars (`family_and_style_max_length` FAIL). | Unified `STAT` on `SmText` (max 30 chars) and stamped `27.000` / `Version 27.000;27.0.0.0` across all 5 binaries. |
| **P0** | **Resolved (`27.0.0.0`)** | `Sans`, `Rounded`, `Mono` | Empty `STAT` axis values (`inconsistencies_between_fvar_STAT` FAIL & `family_and_style_max_length` ERROR). | Added `ensure_stat()` in `scripts/common.py` emitting full `STAT` tables (11 / 10 / 5 axis values); added PostScript names on all 9 `Rounded` instances. |
| **P1** | **Deferred (`27.0.0.0` kept as-is)** | Family brand | **Strata** is the product-anchored family name (`Strata`, `Aurora`, and `Solstice` share one identity in `strata-weather/DESIGN.md`). | Kept **Strata** for `27.0.0.0`. Rename remains cheap in `scripts/common.py` before any multi-app rebrand. |
| **P1** | **Deferred (adapter needed)** | Icons (`data-layer`) | `bolt` vs `--icon-tone-storm`, `ice` has no dedicated app token, `heat` vs `--icon-tone-hot`, and **`cold.svg` puts its thermometer on `data-layer="heat"`**. | Handle via CSS/component layer mapping in `strata-weather` (override `cold`'s thermometer stroke), or split `cold`/neutral thermometer layer in `27.1.0.0`. |
| **P1** | **Deferred (adapter needed)** | Icons (conditions) | `ConditionGlyph` mismatches: `heat` vs `hot`; `rain-day`/`rain-night`/`showers` vs `showers-day`/`showers-night`; missing `haze` & `unknown`. | Map in `strata-weather` adapter or align slugs in `27.1.0.0`. |
| **P2** | **Tracked** | Cross-face & icon polish | `Strata Sans Rounded` (3 words) & `sans-rounded`/`rounded` internal key; `StrataMono` default `Light` (`wght=300`); `Semibold` vs `SemiBold`; `Optical size` vs `Optical Size`; upstream vendor IDs; Mono unlabeled/duplicate `cv*` labels; `thermometer`/`bell`/`clock` object names; `UvIndexIcon` casing; `StrataIcons.woff2` `i0`–`i70` glyphs & shifting PUA codepoints. | Tracked below; apply selectively in `27.1.0.0+`. |

---

## Part 1: Font Names Review

### 1.1 Family & Face Brand Names (Kept for `27.0.0.0`)

| Face Key (`build.py`) | Key (`site.py`) | Family Name | File Stem | Assessment |
| --- | --- | --- | --- | --- |
| `sans` | `sans` | `Strata Sans` | `StrataSans` | Clean, concise, clear. |
| `sans-rounded` | `rounded` | `Strata Sans Rounded` | `StrataSansRounded` | Clear lineage to `Strata Sans` (parallels *SF Pro Rounded*), though 3 words while siblings are 2 words and `site.py` uses key `rounded`. `Strata Sans Rounded ExtraLight` is 30 chars (passes 31-char GDI limit). |
| `serif` | `serif` | `Strata Serif` | `StrataSerif` | Clean, concise, clear. |
| `mono` | `mono` | `Strata Mono` | `StrataMono` | Clean, concise, clear. |
| `icons` | `icons` | `Strata Icons` | `StrataIcons` | Clean, concise, clear. |

**Key notes:**
- **Reserved Font Name (RFN) compliance:** **PASS.** Zero occurrences of `Inter`, `Source`, or `Fira` in any compiled binary `name` table.
- **External trademark landscape:** Commercial third-party fonts named "Strata" / "Strata Pro" exist outside OFL; no conflict with upstream OFL licenses, noted for awareness if trademarking.
- **Future sibling names:** Bookmarked math face fits naturally as **`Strata Math`** (`StrataMath`), and Nerd Font patch as **`Strata Mono NF`** (`StrataMonoNF`).

---

### 1.2 Compiled `27.0.0.0` OpenType Metadata (Verified Post-Fix)

| Field | Strata Sans | Strata Sans Rounded | Strata Serif | Strata Mono | Strata Icons |
| --- | --- | --- | --- | --- | --- |
| `head.fontRevision` | `27.000` | `27.000` | `27.000` | `27.000` | `27.000` |
| `name` ID 1 (Family) | `Strata Sans` | `Strata Sans Rounded` | `Strata Serif` | `Strata Mono` | `Strata Icons` |
| `name` ID 2 (Subfamily) | `Regular` | `Regular` | `Regular` | `Regular` | `Regular` |
| `name` ID 3 (Unique ID) | `StrataSans-Regular;27.0.0.0` | `StrataSansRounded-Regular;27.0.0.0` | `StrataSerif-Regular;27.0.0.0` | `StrataMono-Light;27.0.0.0` | `StrataIcons-Regular;27.0.0.0` |
| `name` ID 4 (Full Name) | `Strata Sans Regular` | `Strata Sans Rounded Regular` | `Strata Serif Regular` | `Strata Mono Light` | `Strata Icons Regular` |
| `name` ID 5 (Version) | `Version 27.000;27.0.0.0` | `Version 27.000;27.0.0.0` | `Version 27.000;27.0.0.0` | `Version 27.000;27.0.0.0` | `Version 27.000;27.0.0.0` |
| `name` ID 6 (PostScript) | `StrataSans-Regular` | `StrataSansRounded-Regular` | `StrataSerif-Regular` | `StrataMono-Light` | `StrataIcons-Regular` |
| `fvar` instances | 18 (18 unique) | 9 (9 unique, all PS-named) | 30 (30 unique) | 5 (5 unique) | *(static)* |
| `STAT` AxisValues | 11 (`Text`/`Display` + 9 weights) | 10 (`Text` + 9 weights) | 14 (`SmText` ≤ 31 chars) | 5 (5 weights) | *(none)* |
| FontBakery metadata FAIL/ERROR | **0** | **0** | **0** | **0** | N/A |

**Remaining P2 metadata polish (optional for `27.1.0.0+`):**
1. **`Strata Mono` default `wght=300` (`Light`):** Valid OpenType (FontBakery passes), but unstyled desktop usage defaults to Light (`300`). CSS consumers should set `font-weight: 400`.
2. **Weight & axis casing:** `Strata Serif` spells weight 600 as `Semibold` (others: `SemiBold`), and `Strata Sans`/`Rounded` name `opsz` `"Optical size"` (Serif: `"Optical Size"`).
3. **Upstream manufacturer/vendor IDs (`name` IDs 8/9/11/12, `OS/2.achVendID`):** Still carry upstream `rsms`/`RSMS`, `Adobe`/`ADBO`, `Carrois Corporate`/`CTDB` (and `NONE` on Rounded). Keep upstream author credits in `licenses/` and `COPYRIGHT.txt`; consider updating Manufacturer/Vendor IDs to Cazco Industries in a later release.
4. **OpenType feature UI labels:**
   - `Strata Sans`: `cv08` reads `"Upper-case i without serif"` vs `ss09` `"Upper-case i without serifs"`; `Strata Sans Rounded` leaves `cv08` unlabeled.
   - `Strata Mono`: 18 `cv*` features (`cv03`–`cv14`, `cv17`–`cv18`, `cv30`–`cv31`) are unlabeled (`None`), `cv16` and `cv29` share the label `'Hexagonal asterisk'`, and capitalization varies (`'alternate lowercase a'` vs `'Lightweight Dollar Sign'`).

---

## Part 2: Icon Names Review (`r15-icons`, 71 Icons)

All 71 filenames in `candidates/r12-type/icons/` match `[a-z][a-z0-9-]*` with zero duplicates and zero React component name collisions (`<PascalCase>Icon`, cleanly avoiding JS global collisions like `MapIcon`).

### 2.1 Alignment Findings for `strata-weather` Integration (P1)

#### 1. `data-layer` names vs. `--icon-tone-*` CSS tokens

| `r15-icons` `data-layer` | Strata-Weather `--icon-tone-*` | Alignment & Notes |
| --- | --- | --- |
| `sun`, `moon`, `cloud`, `rain`, `snow`, `fog` | Exact matches | Ready to map 1:1. *(Note: `r15` `thunderstorm` dropped its `rain` layer and uses `cloud` + `bolt` only.)* |
| `wind` | `--icon-tone-wind` | Name matches, but `tornado` and `hurricane` use `data-layer="wind"` while `strata-weather` tints them `--icon-tone-storm`; `air-quality` ("AQI") also uses `wind`. |
| `bolt` | `--icon-tone-storm` | Name mismatch — map `[data-layer="bolt"]` → `--icon-tone-storm`. |
| `ice` | *(none)* | Map `[data-layer="ice"]` → `--icon-tone-cold` or `--icon-tone-snow`. |
| `heat` | `--icon-tone-hot` | **Mismatch + `cold.svg` quirk:** `cold.svg` wraps its thermometer tube in `data-layer="heat"` (with the snowflake in `snow`). Without a `cold`-specific override, multi-tone CSS turns the Cold thermometer orange. (`thermometer.svg` and `dew-point.svg` also put the thermometer in `heat`; `pressure` and `visibility` carry no layer.) |

#### 2. Condition slug mismatches against `strata-weather` (`condition-glyph.ts` & `inventory/icons.json`)

| `strata-weather` Name | `r15-icons` Name | Notes |
| --- | --- | --- |
| `hot` (`ConditionGlyph`) | `heat` | Part-of-speech mismatch (`heat`/`cold` vs app's `hot`/`cold`). Map `hot → heat` in adapter, or add/rename in `27.1.0.0`. |
| `showers-day`, `showers-night` | `showers`, `rain-day`, `rain-night` | `r15-icons` provides neutral `showers` + day/night `rain` & `snow`; map `showers-day` → `rain-day` / `showers-night` → `rain-night` or add dedicated shower composites. |
| `heavy-rain` vs `rain-heavy-*` | `heavy-rain` | `r15-icons`'s `heavy-rain` matches `ConditionGlyph`; `scripts/inventory.py` used `rain-heavy-*` and should adopt adjective-first (`light-rain`, `heavy-rain`). |
| `haze`, `unknown` | *(not yet drawn)* | Two of Strata-Weather's 25 `ConditionGlyph` values remain to be drawn before full cutover. |

### 2.2 Convention Findings (P2)

- **Object vs. semantic naming:** Most metrics and app chrome use semantic/quantity names (`pressure`, `visibility`, `humidity`, `today`, `places`, `delete`, `add`, `close`), while `thermometer`, `bell`, `clock`, and `umbrella` use physical object names. Keep all four as canonical short names and document the split clearly.
- **Acronym casing (`UvIndexIcon`):** `scripts/icons.py` generates `UvIndexIcon` (matching modern TS libraries like Lucide) rather than `UVIndexIcon`.
- **5-tier alert hierarchy:** `alert` (rounded square), `alert-advisory` (circle — visually close to `info`), `alert-watch` (diamond), `alert-warning` (triangle), `alert-emergency` (siren).
- **Directional & overflow extensibility:** `chevron-{up,down,left,right}` is a complete 4-way set; `back` (`←`) and `more` (`⋯`) are clear, with `arrow-*` and `more-vertical` reserved if expanded later.
- **Icon font (`StrataIcons.woff2`):** Compiled glyph names are positional (`i0`–`i70`) and PUA codepoints (`U+E000`–`U+E046`) shift alphabetically whenever icons are added. Treat SVG/React TSX as primary; pin an append-only codepoint registry if `StrataIcons.woff2` ever becomes a direct consumer API.

---

## Part 3: Recommended Naming Rules Going Forward

1. **Font family & face names:**
   - Pattern: `<Family> <Style>` (`Strata Sans`, `Strata Serif`, `Strata Mono`, `Strata Icons`, `Strata Math`).
   - Never use upstream Reserved Font Names (`Inter`, `Source`, `Fira`) in any name record, filename, URL, or instance PostScript name.
   - Keep `ID 16 + " " + STAT style` ≤ **31 characters** across every optical size × weight combination.
   - Standardize new weight names to `Thin`, `ExtraLight`, `Light`, `Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`, `Black`; axis names to `Weight` (`wght`) and `Optical Size` (`opsz`).
2. **Icon filenames & React exports:**
   - Lowercase kebab-case ASCII only: `[a-z][a-z0-9-]*`.
   - React export rule: split on `-`, capitalize first letter of each token (`uv-index` → `UvIndexIcon`), append `Icon`.
   - Day/night variants always suffix `-day` or `-night` (`<condition>-day`, `<condition>-night`).
   - Intensity modifiers precede the noun (`light-rain`, `heavy-rain`, `light-snow`, `heavy-snow`).
   - Alert tiers prefix `alert-`; directional sets prefix the shape (`chevron-*`, `arrow-*`).
3. **Icon `data-layer` values:**
   - Only place `data-layer` on `<g>` elements.
   - Avoid tagging neutral or cold instruments with `data-layer="heat"` in future icons.
