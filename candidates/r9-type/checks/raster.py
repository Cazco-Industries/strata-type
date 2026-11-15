"""Small raster helpers for the candidate checks: shaped text and single
glyphs drawn from the built variable fonts with FreeType (no hinting,
greyscale antialiasing, sub-pixel pen positions), so measurements follow
unhinted screen text closely.

Nothing here writes into the candidate; the checks only read build output.
"""
import freetype
import uharfbuzz as hb
from PIL import Image, ImageChops

FLAGS = freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_NO_BITMAP | freetype.FT_LOAD_TARGET_NORMAL


class Face:
    def __init__(self, path):
        self.path = str(path)
        self.ft = freetype.Face(self.path)
        self.hbface = hb.Face(hb.Blob.from_file_path(self.path))
        self.upem = self.hbface.upem
        self.axes = []
        if self.ft.has_multiple_masters:
            self.axes = [(a.tag, a.minimum, a.default, a.maximum) for a in self.ft.get_variation_info().axes]

    def location(self, size, wght=400):
        """CSS-like location: opsz follows the pixel size (clamped), wght as given."""
        loc = {}
        for tag, lo, default, hi in self.axes:
            v = {'opsz': size, 'wght': wght}.get(tag, default)
            loc[tag] = max(lo, min(hi, v))
        return loc

    def _set(self, size, loc):
        if self.axes:
            self.ft.set_var_design_coords(tuple(loc.get(t, d) for t, _, d, _ in self.axes))
        self.ft.set_char_size(int(round(size * 64)))

    def shape(self, text, size, loc, features=None):
        """[(glyph id, x px, y px)] and the ink extent (left, right) in px."""
        font = hb.Font(self.hbface)
        font.scale = (self.upem, self.upem)
        if loc:
            font.set_variations(loc)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, features or {})
        k = size / self.upem
        out, x = [], 0
        left = right = None
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gx = (x + pos.x_offset) * k
            out.append((info.codepoint, gx, pos.y_offset * k))
            ext = font.get_glyph_extents(info.codepoint)
            if ext and ext.width:
                lo = gx + ext.x_bearing * k
                hi = lo + ext.width * k
                left = lo if left is None else min(left, lo)
                right = hi if right is None else max(right, hi)
            x += pos.x_advance
        return out, (left or 0.0, right or 0.0), x * k

    def draw(self, canvas, glyphs, size, loc, ox, baseline):
        """Draw shaped glyphs on an 'L' canvas, pen origin at (ox, baseline)."""
        self._set(size, loc)
        for gid, gx, gy in glyphs:
            x = ox + gx
            ix = int(x // 1)
            fx = x - ix
            self.ft.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(int(round(fx * 64)), 0))
            self.ft.load_glyph(gid, FLAGS)
            self.ft.glyph.render(freetype.FT_RENDER_MODE_NORMAL)
            bm = self.ft.glyph.bitmap
            if not bm.width or not bm.rows:
                continue
            data = bytes(bm.buffer) if bm.pitch == bm.width else b''.join(
                bytes(bm.buffer[r * bm.pitch:r * bm.pitch + bm.width]) for r in range(bm.rows))
            img = Image.frombytes('L', (bm.width, bm.rows), data)
            px = ix + self.ft.glyph.bitmap_left
            py = int(round(baseline - gy)) - self.ft.glyph.bitmap_top
            region = (px, py, px + bm.width, py + bm.rows)
            under = canvas.crop(region)
            canvas.paste(ImageChops.lighter(under, img), region)
        self.ft.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(0, 0))

    def text(self, text, size, loc, features=None, pad=None, centre=None, canvas=None, baseline=None):
        """Render a string. With centre=(w, h), the ink is centred
        horizontally on a w x h canvas with the baseline at 0.75 h."""
        glyphs, (left, right), adv = self.shape(text, size, loc, features)
        if centre:
            w, h = centre
            canvas = canvas or Image.new('L', (w, h), 0)
            baseline = baseline if baseline is not None else round(0.75 * h)
            ox = w / 2 - (left + right) / 2
        else:
            pad = size if pad is None else pad
            w = int(adv + 2 * pad) + 1
            h = int(size * 1.6 + 2 * pad)
            canvas = canvas or Image.new('L', (w, h), 0)
            baseline = baseline if baseline is not None else round(pad + size * 1.05)
            ox = pad
        self.draw(canvas, glyphs, size, loc, ox, baseline)
        return canvas


def total(img):
    return sum(i * n for i, n in enumerate(img.histogram()))


def xor(a, b):
    """Coverage difference of two equal-size 'L' images: sum |a - b| over
    sum max(a, b). 0 = identical, 1 = no shared ink."""
    den = total(ImageChops.lighter(a, b))
    return total(ImageChops.difference(a, b)) / den if den else 0.0


def count(img):
    """Pixels set in a thresholded ('L', 0/255) image."""
    return img.histogram()[255]
