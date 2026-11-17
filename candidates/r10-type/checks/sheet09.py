"""Mono units on render file 09 (the specimen's '℉ / °F  ℃ / °C' row, 2x), per component.
usage: sheet09.py PNG [y0 y1]   (python with numpy, scipy and Pillow; PNG is render sheet 09)
r10 adds, per unit, on the raster itself (device px, gray < 140 is ink):
the ring's side walls on its middle scanline (dark run, and soft width as
summed coverage), the counter area (enclosed
non-ink px), the letter's ink width over the typed letter's (C and F, and
their difference), and the clearances: ring to letter, unit to the next
ink in the row, and the figure-free gap to the typed degree pair."""
import sys, math
import numpy as np
from PIL import Image
from scipy import ndimage

def soft(m):
    return float(m.max(axis=0).sum()) / 2, float(m.max(axis=1).sum()) / 2

def gap(a, b, t=0.5):
    A, B = a >= t, b >= t
    if (A & B).any():
        return 0.0
    pa = np.argwhere(A).astype(np.float32); pb = np.argwhere(B).astype(np.float32)
    d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1)).min()
    return float(max(d - 1, 0) / 2)

def walls(m):
    cy = (m.sum(axis=1) * np.arange(m.shape[0])).sum() / m.sum()
    cx = (m.sum(axis=0) * np.arange(m.shape[1])).sum() / m.sum()
    def prof(p):
        nz = np.nonzero(p > 0.02)[0]
        p = p[nz.min():nz.max()+1]
        lo, hi = max(1, len(p)//4), min(len(p)-1, len(p) - len(p)//4)
        k = lo + int(np.argmin(p[lo:hi]))
        return float(p[:k].sum() + p[k]/2) / 2, float(p[k+1:].sum() + p[k]/2) / 2
    r0 = int(math.floor(cy)); fr = cy - r0
    row = m[r0] * (1 - fr) + m[min(r0+1, m.shape[0]-1)] * fr
    c0 = int(math.floor(cx)); fc = cx - c0
    col = m[:, c0] * (1 - fc) + m[:, min(c0+1, m.shape[1]-1)] * fc
    l, r = prof(row); t, b = prof(col)
    return (l + r) / 2, (t + b) / 2

def opening(m, t=0.5):
    """The C's opening (css px), as strip.py measures it: the vertical blank
    between its arms, one device pixel inside their common right edge."""
    ys, xs = np.nonzero(m >= t)
    ymid = (ys.min() + ys.max()) / 2
    xr = min(xs[ys < ymid].max(), xs[ys > ymid].max())
    vals = []
    for x in (xr - 2, xr - 1):
        col = m[:, x]; inkr = np.nonzero(col >= t)[0]
        a, b = inkr[inkr < ymid], inkr[inkr > ymid]
        if len(a) and len(b):
            vals.append(float((1 - col[a.max():b.min() + 1]).sum()))
    return min(vals) / 2 if vals else None

png = sys.argv[1]
y0, y1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (3400, 3500)
a = np.asarray(Image.open(png).convert('L'), dtype=np.float32)
GRAY = 140
bg = np.median(a[y0 - 10, :])
fg = float(np.percentile(a[y0:y1], 0.5))  # text colour (#172529), so full ink is 1.0
ink = np.clip((bg - a[y0:y1]) / (bg - fg), 0, 1)
ink[:, :40] = 0
lab, n = ndimage.label(ink > 0.02)
objs = ndimage.find_objects(lab)
comps = sorted(((s[1].start, i + 1, s) for i, s in enumerate(objs)), key=lambda x: x[0])
masks = []
for x, i, s in comps:
    m = np.where(lab == i, ink, 0)
    if m.sum() < 20:
        continue
    masks.append(m)
# expected order: ring(℉) F(℉) / ° F  ring(℃) C(℃) / ° C
assert len(masks) == 10, len(masks)
names = ['ringF', 'letF', 'slash1', 'degF', 'F', 'ringC', 'letC', 'slash2', 'degC', 'C']
M = dict(zip(names, masks))
def crop(m):
    ys, xs = np.nonzero(m > 0.02)
    return m[ys.min():ys.max()+1, xs.min():xs.max()+1]
for u, ring, let, deg, L in (('℉', 'ringF', 'letF', 'degF', 'F'), ('℃', 'ringC', 'letC', 'degC', 'C')):
    rw, rh = soft(crop(M[ring])); dw, dh = soft(crop(M[deg]))
    lw, lh = soft(crop(M[let])); tw, th = soft(crop(M[L]))
    rs, rt = walls(crop(M[ring])); ds, dt = walls(crop(M[deg]))
    size = th / (1393 / 1950)  # F cap height 1393 / 1950
    print(f'{u}: size ~{size:.1f} px; ring {rw:.2f} x {rh:.2f} css px, aspect {rw/rh:.3f}; ring/° height {rh/dh:.3f}; '
          f'walls side {rs/ds:.3f} top {rt/dt:.3f} of °; letter height {lh/th:.3f}, width {lw/tw:.3f} of typed {L}; '
          f'ring-letter gap {gap(M[ring], M[let]):.2f} css px ({gap(M[ring], M[let]) * 13 / size:.2f} px scaled to 13 px)')
lc, tc = opening(crop(M['letC'])), opening(crop(M['C']))
print(f'C opening: unit letter {lc:.2f} css px, typed C {tc:.2f} css px, ratio {lc / tc:.3f}')


# r10: raster walls and counter (threshold gray < 140), ratios, clearances
lab_full = lab
def bbox(m):
    ys, xs = np.nonzero(m > 0.02)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
idx = {}
for k, (x, i, sl) in enumerate([c for c in comps if np.where(lab == c[1], ink, 0).sum() >= 20]):
    idx[names[k]] = i
row = a[y0:y1]
res = {}
for u, ring, let, L, nxt in (('℉', 'ringF', 'letF', 'F', 'slash1'), ('℃', 'ringC', 'letC', 'C', 'slash2')):
    y_0, y_1, x_0, x_1 = bbox(M[ring])
    sub = row[y_0:y_1, x_0:x_1]
    own = lab[y_0:y_1, x_0:x_1] == idx[ring]
    dark = (sub < GRAY) & own
    mid = (y_0 + y_1 - 1) / 2 - y_0
    rows_ = [int(math.floor(mid)), int(math.ceil(mid))]
    sides, soft_ = [], []
    cov = np.where(own, ink[y_0:y_1, x_0:x_1], 0)
    for r_ in sorted(set(rows_)):
        xs = np.nonzero(dark[r_])[0]
        runs = np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1) if len(xs) else []
        if len(runs) >= 2:
            sides.append((len(runs[0]), len(runs[-1])))
        h_ = cov.shape[1] // 2
        soft_.append((float(cov[r_, :h_].sum()), float(cov[r_, h_:].sum())))
    filled = ndimage.binary_fill_holes(dark)
    counter = int((filled & ~dark).sum())
    lw = soft(crop(M[let]))[0]; tw = soft(crop(M[L]))[0]
    clear_next = gap(M[let] + M[ring], M[nxt])
    res[u] = dict(wall=max(max(s_) for s_ in sides) if sides else None, sides=sides, counter=counter,
                  soft=max(max(s_) for s_ in soft_) if soft_ else None,
                  ratio=lw / tw, ring_letter=gap(M[ring], M[let]), next=clear_next)
for u, r in res.items():
    print(f"{u}: middle-scanline wall {r['wall']} raster px (left/right {r['sides']}; soft wall, summed coverage, "
          f"max {r['soft']:.2f} px: a soft wall of 1.99 px or more can give a 3 px run at another phase), "
          f"counter {r['counter']} raster px, "
          f"letter width {r['ratio']:.3f} of typed, ring-letter clearance {r['ring_letter']:.2f} css px, "
          f"clearance to the next ink {r['next']:.2f} css px")
print(f"C/F width ratios: C {res['℃']['ratio']:.3f}, F {res['℉']['ratio']:.3f}, difference {abs(res['℃']['ratio'] - res['℉']['ratio']):.3f}")
print('acceptance: wall <= 2.5 raster px:', all(r['wall'] is not None and r['wall'] <= 2.5 for r in res.values()),
      '| counter >= 38:', all(r['counter'] >= 38 for r in res.values()),
      '| C ratio >= 0.77:', res['℃']['ratio'] >= 0.77,
      '| ratios within 0.04:', abs(res['℃']['ratio'] - res['℉']['ratio']) <= 0.04)
