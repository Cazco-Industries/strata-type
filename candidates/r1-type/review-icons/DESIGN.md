# Strata icons

A rounded outline family with a low left cloud roll, a broad off-centre crown and a long, gently stepped right shoulder. The weather silhouette is shared across conditions. Small, clear spaces take priority over ornamental detail.

## Grid, keylines and weight

- Every SVG has a 24 × 24 view box. Use quarter-unit anchors where practical; fractional curve coordinates are optical corrections.
- One stroke: **1.875 units**, including every interior mark. At 16 / 20 / 24 / 32 px this becomes 1.25 / 1.5625 / 1.875 / 2.5 px. Scale the complete drawing, including its stroke.
- The main enclosing keyline is 2.75–21.25. Circular enclosures have radius 9. Weather symbols may use optical overshoot, including partly cloudy rays at 1 and flake tips near 23; the complete painted stroke remains inside the view box.
- Narrow actions keep smaller apparent dimensions. A chevron, plus and close symbol should not expand to the size of a calendar, circle or warning enclosure.
- No transforms, fixed screen-pixel strokes, embedded styles, masks, raster content or per-part stroke widths. Every SVG defaults to `fill="none"` and `stroke="currentColor"`.

## Caps, corners and counters

All caps and joins are round. Enclosing corners use curves rather than depending entirely on a rounded join. Keep straight runs long enough to survive a 16 px raster. Tiny intentional pellet marks use very short round-capped strokes; they do not introduce a second weight or a separate fill treatment.

Treat the full stroke envelope as occupied space. A 3.375-unit separation between centre lines leaves 1.5 units of clear space after two half strokes: **1 CSS px at 16 px**. Separate cloud and precipitation by at least this amount. Deliberate connections within a single symbol are exempt; the storm bolt deliberately passes through the interrupted cloud base.

The two hail stones have 2.25-unit radii. Each clear counter is 2.625 units across before rasterisation, or 1.75 px at 16 px. Do not replace these with small counters or a level row of three dots. The snowflake has a 2.5-unit hexagonal core and 4-unit radial tips; the central opening remains distinct from its arms. Its centre is at y = 18.9.

## Weather construction

The standard cloud runs from x = 2.75 to 21.25, with its crown at y = 2.75 and base at y = 12.25. Its small left roll leads into a broad crown displaced right of centre. The right edge steps down into a softer low shoulder. Reuse the contour rather than drawing a new cloud for each condition.

Cloud-only placement shifts the contour down 3.25 units. Celestial composites scale the same contour uniformly to 0.89 or 0.81 and position it lower. Snow and wintry mix compress its height to 92.105263 percent, retaining the crown at 2.75 and raising the base to 11.5; this reserves enough room for a larger, genuinely open flake. These are compositional adjustments to one contour, not independent silhouettes.

- **Clear day / partly cloudy day:** circular solar body or visible circular arc, with detached rays. The nearest ray centre line is at least 3.375 units from the solar rim. The partly cloudy arc stops before the foreground cloud; rays never join the rim.
- **Clear night / partly cloudy night:** plain crescent; the composite uses an interrupted crescent with generous separation from the smaller cloud. Do not bridge the moon tips into the cloud.
- **Fog:** two offset horizontal bands at 16.5 and 20.5. The top band has 1.583 px of clear space below the cloud at 16 px.
- **Drizzle:** three short slanted dashes, 2.61 units long before round caps. **Rain:** three longer slanted strokes, 4.74 units long. **Heavy rain:** four strokes, 5.53 units long. The dashes are visibly longer than the solid pellets used for sleet.
- **Sleet:** four small solid pellets, staggered across two heights. It means ice pellets, without a rain stroke or snowflake. **Hail:** two much larger hollow stones at different heights. Their counters and size distinguish them from sleet.
- **Snow:** one open-centred six-point flake. **Wintry mix:** a rain stroke on the left and the same flake on the right. Both components remain separate in the 16 px monochrome raster.
- **Thunderstorm:** a 13-unit-tall open zigzag bolt. Its upper stroke enters the cloud and its lower stroke extends well below the base. The cloud base is interrupted to expose the bolt. Two shorter outer rain strokes remain secondary.
- **Wind / tornado / thermometer:** retained flowing currents, tapering bands and broad-bulb thermometer constructions.
- **Humidity:** a large water drop with one internal contour. **Sunrise / sunset:** the same half sun and horizon, with an explicit upward or downward arrow. **Umbrella:** a curved canopy with three scalloped sections and a hooked shaft.

## Interface construction

Today is a bound calendar with a clear header and one circled day. It contains no roof or house silhouette. Radar uses three concentric range arcs at radii 2 / 5.5 / 9, with a fully bounded quarter-circle sweep wedge. No isolated radial hand or broken outer C carries the meaning alone.

The existing search, places, settings, alert, share, add, close, chevron, location and layer constructions retain their geometry. New notification, clock and playback symbols use the same stroke and curve logic. Play and pause remain outlines rather than introducing a heavier filled style.

## Layer contract

Every weather part is in a named `g` group. Allowed layer values are `sun`, `moon`, `cloud`, `rain`, `snow`, `ice`, `bolt`, `wind`, `fog` and `heat`. `icon-layers.json` records the group order. Interface symbols do not require weather groups.

Sleet and hail use `ice`; wintry mix uses separate `rain` and `snow` groups. The thermometer uses `heat`. Humidity and umbrella use `rain`. Sunrise and sunset use `sun`, including the directional arrow. Preserve `data-layer` attributes when copying the SVGs. No meaning depends on optional colour, which is applied only at render time.

## Extension rules

1. Begin with the closest existing construction. Reuse the cloud, crescent, solar arc, precipitation angle, flake and keylines.
2. Establish a recognisable silhouette in monochrome at 16 px before adding details. Frozen types must differ in shape, size and arrangement, not simply dot count.
3. Keep the common stroke. Remove details or enlarge an open counter before thinning an individual path. Any future weight must cover the complete library as a separate set.
4. Keep adjacent symbols optically balanced rather than mathematically identical in area. Check narrow actions, circular enclosures and compound weather symbols together.
5. New weather composites must preserve the layer vocabulary and at least 1 px of cloud-to-precipitation clearance at 16 px. Interrupt background outlines when a foreground part intentionally crosses them; never paint them out with a background colour.
6. New day/night conditions replace only the celestial component and preserve the weather condition. Sun rays always detach from the visible rim.
7. Render every addition at 16 / 20 / 24 / 32 px on light and dark, at ordinary and doubled pixel density. Check 16 / 20 / 24 px icons beside 13 / 15 / 17 px regular interface text, respectively. Inspect the actual-size result as well as a pixel loupe.
8. Update sources, licences, the layer manifest, change record and review evidence whenever the library grows. Preserve all established file names.

## Evidence and scope

`before/icons/` freezes the exact 28 incoming SVGs; `baseline-sha256.json` records the copied input assets and notices. `review/before-{16,20,24,32}.png` and `review/after-{16,20,24,32}.png` use identical slots and include both light and dark surfaces. The nine additions are explicitly absent from the before sheets. Additional sheets cover text pairing, answer-card mockups, 16 px pixel loupes, layer tones and doubled density. All 18 final sheets were reopened for the review recorded in `SELF-REVIEW.md`.

This is a local icon deliverable. The preview text uses an installed neutral interface face; pairing with final Strata Sans and ordinary-user recognition have not been tested. Colour examples are review aids, not an approved product palette. No app integration or deployment is included.
