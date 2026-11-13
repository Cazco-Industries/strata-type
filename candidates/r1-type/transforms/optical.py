"""Optical kerning for figures: gaps measured from outline profiles.

The gap between two glyphs is measured as the mean horizontal white between
the right profile of the first and the left profile of the second, sampled
over a vertical band and clipped (so deep counters do not count as white the
eye sees). Kerning is set so a pair's gap matches a reference pair's gap.
"""
import lib


def profile(font, name, lo, hi, n=48):
    g = font[name]
    out = {}
    for i in range(n + 1):
        y = lo + (hi - lo) * i / n
        xs = lib.crossings(g, y, font)
        if xs:
            out[i] = (xs[0], xs[-1])
    return out


def ink_band(font, name):
    b = lib.bounds(font[name], font)
    return b[1], b[3]


def raw_gap(font, a, b, lo, hi, clip):
    """Mean clipped gap with no kerning, or None if the band misses one glyph."""
    pa, pb = profile(font, a, lo, hi), profile(font, b, lo, hi)
    w = font[a].width
    gs = []
    for i in range(49):
        ra = pa.get(i, (None, None))[1]
        lb = pb.get(i, (None, None))[0]
        if ra is None and lb is None:
            continue
        if ra is None or lb is None:
            gs.append(clip)
            continue
        gs.append(min(lb + w - ra, clip))
    return sum(gs) / len(gs) if gs else None


def bbox_gap(font, a, b):
    ba, bb = lib.bounds(font[a], font), lib.bounds(font[b], font)
    return bb[0] + font[a].width - ba[2]


def degree_kerns(font, figures, degree='degree', ref='zero'):
    """Kerning (figure, degree) so every figure sits as far from the ring as
    the zero does, and never closer at its widest point."""
    lo, hi = ink_band(font, degree)
    clip = 0.6 * (hi - lo)
    target = raw_gap(font, ref, degree, lo, hi, clip)
    target_box = bbox_gap(font, ref, degree)
    out = {}
    for x in figures:
        g = raw_gap(font, x, degree, lo, hi, clip)
        k = target - g
        k = max(k, target_box - bbox_gap(font, x, degree))
        out[(x, degree)] = round(k)
    return out


def pair_kerns(font, pairs, ref=('zero', 'zero'), lo_hi=None, limits=(-150, 40), dead=16):
    """Kerning for each pair so its gap over the figure height matches the
    reference pair; tiny corrections are dropped."""
    lo, hi = lo_hi or (0, font.info.capHeight)
    clip = 0.5 * (hi - lo)
    target = raw_gap(font, ref[0], ref[1], lo, hi, clip)
    # never closer at the nearest points than 0.8 of the reference's
    floor_box = 0.8 * bbox_gap(font, ref[0], ref[1])
    out = {}
    for a, b in pairs:
        g = raw_gap(font, a, b, lo, hi, clip)
        k = max(limits[0], min(limits[1], target - g), floor_box - bbox_gap(font, a, b))
        out[(a, b)] = round(k) if abs(k) >= dead else 0
    return out
