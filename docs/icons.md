# Strata Icons (`r15-icons`, Release `27.0.0.0`)

Technical reference and complete 71-icon catalog for the finalized **Strata Icons** library (`candidates/r12-type/icons/`, packaged in [`dist/icons/`](../dist/icons/) at annual version **`27.0.0.0`**).

> [!NOTE]
> **Status:** Adopted by owner decision on 2026-11-22 (`r15-icons`, which includes all five owner specimen-site fixes plus the refined single-bolt `thunderstorm`, clear upper-left night crescent, `sunrise`/`sunset`, and 3-rpx snow clearance). Imported into `candidates/r12-type/icons/` and shipped in [`dist/icons/`](../dist/icons/) at `v27.0.0.0`; **not yet wired into `strata-weather`**.

---

## Visual & Technical Specification

Every icon in the 71-icon library adheres to the automated contract enforced by `scripts/icons.py`:

| Property | Contract Value |
| --- | --- |
| **Grid / `viewBox`** | `0 0 24 24` |
| **Stroke width** | `1.875` (`1.25 CSS px` at 16 px; `1.5625 CSS px` at 20 px; `1.875 CSS px` at 24 px) |
| **Caps & joins** | `stroke-linecap="round"`, `stroke-linejoin="round"` |
| **Paint defaults** | `fill="none"`, `stroke="currentColor"` (monochrome by default) |
| **Allowed elements** | `path`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `rect`, `g` |
| **Forbidden** | `transform`, `<mask>`, `<defs>`, `<style>`, embedded raster, `<!DOCTYPE>` / XML entities |
| **Small dots & dot rays** | Circles with `r <= 0.93`, or `0.1`-unit round-capped strokes for dot rays (so browser engines never drop hairline points) |
| **Target sizes** | Designed and measured at `16`, `20`, `24`, and `32 px` on light and dark backgrounds alongside `13–17 px` `Strata Sans` |
| **Clearance gate** | Separate strokes/parts maintain ≥ `1 CSS px` (`2 raster px` at 2×) separation at 16 px; enclosed counters stay open |
| **Shared cloud silhouette** | Precipitation icons share a consistent cloud baseline (`freezing-rain` and `showers` use lifted/compact variants; `thunderstorm` notches the lower cloud edge for its central bolt); day/night composites share identical clouds |

> [!NOTE]
> **Known `r15-icons` snow viewport note:** Translating the full-size six-arm crystal down for 3-raster-px cloud clearance clips a small fraction of the two lowest round caps at `y = 24` (`0.185` grid units on `snow`, `0.074` on `snow-day`/`snow-night`).

---

## Delivery Formats (`dist/icons/`)

1. **Minified SVGs (`dist/icons/svg/<name>.svg`) — Primary format.** Preserves `<g data-layer="…">` groups for optional multi-tone weather coloring.
2. **React TSX components (`dist/icons/react/<PascalCase>Icon.tsx` + `index.ts`) — Recommended for web apps.**
   - Naming rule: split filename stem on `-`, capitalize the first letter of each segment (including acronyms: `uv-index` → `UvIndexIcon`), and append `Icon`.
   - Signature: `export function ClearDayIcon(props: SVGProps<SVGSVGElement>)` with `aria-hidden="true"` by default (pass `aria-label` + `role="img"` and `aria-hidden={undefined}` when an icon conveys standalone meaning).
   - Strictly typechecked against React 19 + TypeScript 5.9 (`make gate`: `tsx_typecheck: PASS`).
3. **Icon font (`dist/icons/StrataIcons.woff2` + `dist/icons/manifest.json`) — Monochrome fallback only.**
   - Built by stroke-expanding every SVG centerline into filled outlines (`1000` UPM, ascent `850`, descent `-150`, `Version 27.000;27.0.0.0`, `8,104` bytes). Ignores `data-layer` groups.
   - **macOS rendering rule:** Always apply `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;` wherever `StrataIcons.woff2` renders. Without it, macOS text dilation draws glyphs 16–19% heavier than the SVGs; with it, weight matches within 1.5%.
   - **Codepoint stability warning:** PUA codepoints (`U+E000`–`U+E046`) are assigned alphabetically per build (`manifest.json`), and glyph names are positional (`i0`–`i70`). Do not hardcode codepoints in app CSS/TS; prefer React/SVG exports or read `manifest.json` at build time.

---

## Multi-Tone Weather Layers (`data-layer`)

Weather icons wrap tintable parts in `<g data-layer="…">`. Without CSS overrides, every group inherits `stroke="currentColor"` and renders monochrome.

Ten layer names are allowed by `scripts/icons.py`:

| `data-layer` | Used In (`r15-icons`) | Suggested Strata-Weather Token | Notes / Caveats |
| --- | --- | --- | --- |
| `sun` | `clear-day`, `partly-cloudy-day`, `rain-day`, `snow-day`, `sunrise`, `sunset`, `uv-index` | `--icon-tone-sun` | Direct match. |
| `moon` | `clear-night`, `partly-cloudy-night`, `rain-night`, `snow-night` | `--icon-tone-moon` | Direct match. |
| `cloud` | `cloudy`, `fog`, `drizzle`, `rain*`, `heavy-rain`, `showers`, `thunderstorm`, `snow*`, `sleet`, `freezing-rain`, `wintry-mix`, `hail`, `partly-cloudy-*` | `--icon-tone-cloud` | Direct match. |
| `rain` | `drizzle`, `rain*`, `heavy-rain`, `showers`, `sleet`, `freezing-rain`, `wintry-mix`, `humidity`, `dew-point`, `umbrella`, `flood` | `--icon-tone-rain` | Direct match (`flood` wraps both house and waves in `rain`; `r15` `thunderstorm` has no `rain` layer). |
| `snow` | `snow*`, `wintry-mix`, `cold` | `--icon-tone-snow` | Direct match. |
| `ice` | `hail`, `sleet`, `freezing-rain` | `--icon-tone-snow` or `--icon-tone-cold` | No `--icon-tone-ice` token exists in `strata-weather` yet. |
| `bolt` | `thunderstorm` | `--icon-tone-storm` | Name differs from app's `storm` token. |
| `wind` | `wind`, `wind-gust`, `tornado`, `hurricane`, `air-quality` | `--icon-tone-wind` | Note: `strata-weather` currently tints `tornado` and `hurricane` with `--icon-tone-storm` rather than `--icon-tone-wind`. |
| `fog` | `fog`, `smoke` | `--icon-tone-fog` | Direct match. |
| `heat` | `heat`, `thermometer`, `dew-point`, `cold` | `--icon-tone-hot` | **Caveat:** `cold.svg` places its thermometer tube on `data-layer="heat"` (and snowflake on `snow`). Override `cold`'s thermometer stroke (e.g., `currentColor` or `--icon-tone-cold`) when enabling multi-tone styling (see [naming-review.md](naming-review.md)). |

Example multi-tone CSS helper:

```css
.strata-icon--tinted [data-layer="sun"]   { color: var(--icon-tone-sun); }
.strata-icon--tinted [data-layer="moon"]  { color: var(--icon-tone-moon); }
.strata-icon--tinted [data-layer="cloud"] { color: var(--icon-tone-cloud); }
.strata-icon--tinted [data-layer="rain"]  { color: var(--icon-tone-rain); }
.strata-icon--tinted [data-layer="snow"]  { color: var(--icon-tone-snow); }
.strata-icon--tinted [data-layer="ice"]   { color: var(--icon-tone-cold, var(--icon-tone-snow)); }
.strata-icon--tinted [data-layer="bolt"]  { color: var(--icon-tone-storm); }
.strata-icon--tinted [data-layer="wind"]  { color: var(--icon-tone-wind); }
.strata-icon--tinted [data-layer="fog"]   { color: var(--icon-tone-fog); }
.strata-icon--tinted [data-layer="heat"]  { color: var(--icon-tone-hot); }
```

---

## Complete Icon Catalog (71 Icons)

### 1. Weather Conditions & Sky (26)

| File Stem | React Component | Visual Description (`r15-icons`) | `data-layer`s | Lineage | `ConditionGlyph` Match |
| --- | --- | --- | --- | --- | --- |
| `clear-day` | `ClearDayIcon` | Sun circle with 8 radial rays | `sun` | Original | `clear-day` |
| `clear-night` | `ClearNightIcon` | Crescent moon | `moon` | Original | `clear-night` |
| `partly-cloudy-day` | `PartlyCloudyDayIcon` | Sun arc tucked upper-left behind low cloud with 4 dot rays | `sun`, `cloud` | Original (r14/r15) | `partly-cloudy-day` |
| `partly-cloudy-night` | `PartlyCloudyNightIcon` | Isolated crescent upper-left clear of low cloud | `moon`, `cloud` | Original (r15) | `partly-cloudy-night` |
| `cloudy` | `CloudyIcon` | Single overcast cloud | `cloud` | Original | `cloudy` |
| `fog` | `FogIcon` | Cloud above two shorter staggered mist bars | `cloud`, `fog` | Original (r14/r15) | `fog` |
| `smoke` | `SmokeIcon` | Diagonal rising smoke plume | `fog` | Original | *(app maps to `haze`)* |
| `drizzle` | `DrizzleIcon` | Cloud above two light slanted drizzle marks | `cloud`, `rain` | Original (r12) | `drizzle` |
| `rain` | `RainIcon` | Cloud above three diagonal rain streaks | `cloud`, `rain` | Original | `rain` |
| `rain-day` | `RainDayIcon` | Sun arc + 4 dot rays behind cloud + three rain streaks | `sun`, `cloud`, `rain` | Original (r14/r15) | *(maps to `showers-day`?)* |
| `rain-night` | `RainNightIcon` | Isolated crescent upper-left + cloud + three rain streaks | `moon`, `cloud`, `rain` | Original (r15) | *(maps to `showers-night`?)* |
| `heavy-rain` | `HeavyRainIcon` | Cloud above four bold slanted rain streaks | `cloud`, `rain` | Original (r14/r15) | `heavy-rain` |
| `showers` | `ShowersIcon` | Compact cloud above two hollow rain drops | `cloud`, `rain` | Original (r10) | *(app splits day/night)* |
| `thunderstorm` | `ThunderstormIcon` | Notched cloud above single open 3-segment lightning bolt | `cloud`, `bolt` | Original (r14/r15) | `thunderstorm` |
| `snow` | `SnowIcon` | Cloud above 6-spoke snowflake (3-rpx cloud gap) | `cloud`, `snow` | Original (r15) | `snow` |
| `snow-day` | `SnowDayIcon` | Sun arc + 4 dot rays behind cloud + 6-spoke snowflake | `sun`, `cloud`, `snow` | Original (r15) | *(new variant)* |
| `snow-night` | `SnowNightIcon` | Isolated crescent upper-left + cloud + 6-spoke snowflake | `moon`, `cloud`, `snow` | Original (r15) | *(new variant)* |
| `sleet` | `SleetIcon` | Cloud above two short rain streaks + two solid pellets | `cloud`, `rain`, `ice` | Original (r12) | `sleet` |
| `freezing-rain` | `FreezingRainIcon` | Cloud with hanging icicles + two flanking rain streaks | `cloud`, `rain`, `ice` | Original (r10, retained in r15) | `freezing-rain` |
| `wintry-mix` | `WintryMixIcon` | Cloud above one rain streak + one 6-spoke snowflake | `cloud`, `rain`, `snow` | Original | *(app maps to `sleet`)* |
| `hail` | `HailIcon` | Cloud above two hollow circular hailstones | `cloud`, `ice` | Original | `hail` |
| `wind` | `WindIcon` | Three curled wind streamlines | `wind` | Original | `wind` |
| `wind-gust` | `WindGustIcon` | Broken-streamline wind burst | `wind` | Original (r10) | *(new variant)* |
| `tornado` | `TornadoIcon` | Tapered funnel vortex | `wind` | Original | `tornado` |
| `hurricane` | `HurricaneIcon` | Eye with two spiral storm arms | `wind` | Original | `hurricane` |
| `flood` | `FloodIcon` | House roofline over two stacked water waves | `rain` | Original | *(hazard icon)* |

### 2. Weather Metrics, Solar & Hazards (12)

| File Stem | React Component | Visual Description (`r15-icons`) | `data-layer`s | Lineage | Notes |
| --- | --- | --- | --- | --- | --- |
| `sunrise` | `SunriseIcon` | Half-sun on horizon with 4 dot rays and upward arrow | `sun` | Original (r14/r15) | Matches `ConditionGlyph` `sunrise`. |
| `sunset` | `SunsetIcon` | Half-sun on horizon with 4 dot rays and downward arrow | `sun` | Original (r14/r15) | Matches `ConditionGlyph` `sunset`. |
| `thermometer` | `ThermometerIcon` | Thermometer tube/bulb with two scale ticks | `heat` | Adapted from Lucide `thermometer` (ISC) | Neutral temperature metric icon. |
| `heat` | `HeatIcon` | Thermometer with rising wavy heat line | `heat` | Adapted from Lucide `thermometer` (ISC) | `ConditionGlyph` calls this `hot` (see [naming-review.md](naming-review.md)). |
| `cold` | `ColdIcon` | Thermometer with 6-spoke snowflake | `heat`, `snow` | Adapted from Lucide `thermometer` (ISC) | Matches `ConditionGlyph` `cold`. See `heat` layer caveat above. |
| `humidity` | `HumidityIcon` | Single water droplet | `rain` | Original | Relative humidity metric. |
| `dew-point` | `DewPointIcon` | Water droplet beside thermometer | `rain`, `heat` | Adapted from Lucide `thermometer` (ISC) | Dew point metric. |
| `pressure` | `PressureIcon` | Barometer dial with needle pointing up-right | *(none)* | Original | Atmospheric pressure metric. |
| `visibility` | `VisibilityIcon` | Eye outline with pupil circle | *(none)* | Original | Horizontal visibility metric. |
| `uv-index` | `UvIndexIcon` | Small sun with 5 radial dot rays (including top-middle ray) above `UV` letterforms | `sun` | Original (r14/r15) | Note PascalCase export is `UvIndexIcon`. |
| `air-quality` | `AirQualityIcon` | Monoline `AQI` letterforms | `wind` | Original (r12) | Wider than precipitation glyphs by design. |
| `umbrella` | `UmbrellaIcon` | Open umbrella | `rain` | Original | Precipitation probability / rain gear indicator. |

### 3. Alerts (5)

Monochrome (`currentColor`); pair with `--severity-*` color tokens and text labels per `strata-weather/DESIGN.md`.

| File Stem | React Component | Container Shape & Visual | NWS / Product Role | Lineage |
| --- | --- | --- | --- | --- |
| `alert` | `AlertIcon` | Exclamation in a **rounded square** | Generic severe-weather / alert trigger | Original |
| `alert-advisory` | `AlertAdvisoryIcon` | Exclamation in a **circle** | NWS Advisory (lowest alert tier) | Original |
| `alert-watch` | `AlertWatchIcon` | Exclamation in a **diamond** | NWS Watch (conditions favorable) | Original |
| `alert-warning` | `AlertWarningIcon` | Exclamation in a **triangle** | NWS Warning (imminent/occurring hazard) | Adapted from Lucide `triangle-alert` (ISC) |
| `alert-emergency` | `AlertEmergencyIcon` | Flashing **siren** | NWS Emergency (extreme life-safety threat) | Adapted from Lucide `siren` (ISC) |

### 4. Navigation, Map & UI Controls (28)

All 28 UI icons are monochrome (`currentColor`, no `data-layer`).

| File Stem | React Component | Visual Description | Lineage | Primary Role |
| --- | --- | --- | --- | --- |
| `today` | `TodayIcon` | Calendar with center dot | Original | Strata Today destination |
| `radar` | `RadarIcon` | Open concentric sweep rings + sweep needle (S2, owner-locked) | Original | Strata Radar destination |
| `places` | `PlacesIcon` | Map pin over curved ground arc | Original | Strata Places destination |
| `map` | `MapIcon` | Three-panel folded map | Original | Map view / regional layer |
| `layers` | `LayersIcon` | Three stacked diamond planes | Adapted from Lucide `layers` (ISC) | Map layer selector |
| `locate` | `LocateIcon` | Crosshair target circle with center dot | Adapted from Lucide `locate-fixed` (ISC) | Use current location |
| `search` | `SearchIcon` | Magnifying glass | Adapted from Lucide `search` (ISC) | Place / settings search |
| `settings` | `SettingsIcon` | Six-lobed rounded gear | Adapted from Hugeicons Free `Settings02Icon` (MIT) | Settings destination |
| `menu` | `MenuIcon` | Three horizontal bars | Original | Navigation menu |
| `more` | `MoreIcon` | Three horizontal dots (`⋯`) | Original | Overflow menu |
| `back` | `BackIcon` | Left-pointing arrow (`←`) | Original | Navigate back |
| `close` | `CloseIcon` | Diagonal cross (`×`) | Adapted from Lucide `x` (ISC) | Dismiss / close |
| `add` | `AddIcon` | Plus sign (`+`) | Adapted from Lucide `plus` (ISC) | Add place / view |
| `check` | `CheckIcon` | Checkmark | Original | Selected / confirmed |
| `edit` | `EditIcon` | Angled pencil | Original | Edit / customize |
| `delete` | `DeleteIcon` | Trash bin with two vertical slats | Original | Delete / remove |
| `refresh` | `RefreshIcon` | Clockwise circular arrow | Original | Manual refresh |
| `share` | `ShareIcon` | Three connected nodes | Adapted from Lucide `share-2` (ISC) | Share link / view |
| `external-link` | `ExternalLinkIcon` | Box with top-right outbound arrow | Original | External authority link |
| `info` | `InfoIcon` | Lowercase `i` in a circle | Original | Information / detail |
| `bell` | `BellIcon` | Notification bell | Original | Notifications |
| `clock` | `ClockIcon` | Analog clock face | Original | Time / forecast history |
| `play` | `PlayIcon` | Right-pointing triangle | Original | Play radar loop |
| `pause` | `PauseIcon` | Two vertical rounded bars | Original | Pause radar loop |
| `chevron-up` | `ChevronUpIcon` | Upward chevron | Companion to Lucide `chevron-right` (ISC) | Collapse / sort up |
| `chevron-down` | `ChevronDownIcon` | Downward chevron | Companion to Lucide `chevron-right` (ISC) | Expand / dropdown |
| `chevron-left` | `ChevronLeftIcon` | Leftward chevron | Companion to Lucide `chevron-right` (ISC) | Previous step |
| `chevron-right` | `ChevronRightIcon` | Rightward chevron | Adapted from Lucide `chevron-right` (ISC) | Drill-in / next step |

---

## Known Coverage Gaps vs. `strata-weather`

Before replacing Lucide and Erik Flowers Weather Icons across the full `strata-weather` app, the following gaps recorded in `inventory/icons.json` remain to be drawn (or mapped):

- **Current `ConditionGlyph` gaps:** `haze`, `showers-day`, `showers-night`, `unknown` (plus resolving `heat` vs `hot`).
- **Planned full weather expansion (`DESIGN-BRIEF.md`):** 8 moon phases (`moon-new` through `moon-waning-crescent`), 4 tide states (`tide-high`, `tide-low`, `tide-rising`, `tide-falling`), `wind-direction`, and intensity/day-night variants as needed.
- **Additional app UI icons:** `strata-weather` currently imports ~182 distinct Lucide icons across `apps/web` and `packages/ui`; `r15-icons` covers the 28 core navigation/control icons and 5 alert icons.

---

## Authoring Rules for Extending the Library

1. **Grid & stroke:** `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="1.875"`, `stroke-linecap="round"`, `stroke-linejoin="round"`. Never mix stroke widths within the set.
2. **Clean SVG markup:** No `transform`, `<mask>`, `<defs>`, `<style>`, or inline hex colors. Keep every path rounded to sensible grid coordinates.
3. **Small-size legibility:** Render and inspect at `16 px` (2×) on both light and dark backgrounds before accepting. Maintain ≥ `1 CSS px` gap between separate components and verify enclosed counters stay visibly open.
4. **Collision check:** Test new icons against existing look-alikes (`alert-advisory` vs `info`, `radar` vs `locate`/`@`, `freezing-rain` vs `rain`/`sleet`, `smoke` vs `fog`, `external-link` vs box-and-diagonal shapes).
5. **Naming:** Follow lowercase kebab-case `[a-z][a-z0-9-]*` and the rules in [naming-review.md](naming-review.md#part-3-recommended-naming-rules-going-forward).
6. **License hygiene:** Never copy, trace, or export SF Symbols or Hugeicons Pro. Any adaptation from Lucide (ISC) or Hugeicons Free Stroke Rounded (MIT) must be logged in `SOURCES.md`, and the bundled notices in `dist/licenses/lucide-LICENSE` and `dist/licenses/hugeicons-free-LICENSE.md` must stay intact.
