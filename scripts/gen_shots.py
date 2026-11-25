"""
Builds every shot of an arc promo onto ONE shared horizon arc, from a JSON shot list.

Each output is a 4480x2400 JPEG: the 3840x2160 (4K) frame plus 320 px of margin
left/right and 240 px on top, so the film can turn each world around the arc's
centre without exposing an edge. The arc is a circle of radius R whose top sits
60% of the way down the frame. Every shot meets that same curve - that is what
makes the match cuts line up.

    python gen_shots.py --config shots.json --raw raw --out public/shots \
        --manifest src/data/manifest.json [--only name1,name2]

Shot types (see references/shot-types.md for every parameter):
    bend        a landscape whose horizon row is wrapped onto the arc ("tiny planet")
    disc        a photo of something round; its circle is scaled onto the arc
    sphere      an equirectangular map rendered as a planet whose limb is the arc
    texture     any texture poured into the disc, with a flat background above
    procedural  drawn in code: blueprint | globe | collage | topo | thin_film
    earth_rise  Earth's night side + a separate sunrise-glow layer (the opening/loop)
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 3840, 2160          # visible 4K frame
MX, MT = 320, 240          # margin left/right, top
EW, EH = W + 2 * MX, H + MT
R = 3700                   # arc radius (px at 4K)
TOP = 1296                 # arc top, frame y (60% of H)
CX, CY = EW / 2, MT + TOP + R
RNG = np.random.default_rng(7)

ys, xs = np.mgrid[0:EH, 0:EW].astype(np.float32)
DX, DY = xs - CX, CY - ys          # DY is "up"
RAD = np.hypot(DX, DY)
THETA = np.arctan2(DX, DY)         # 0 at the top of the arc, + to the right
EDGE = np.clip(R - RAD + 0.5, 0, 1)[..., None]   # anti-aliased disc mask

RAW = '.'


# ----------------------------------------------------------------------------- helpers
def load(name):
    for ext in ('', '.jpg', '.jpeg', '.png', '.JPG', '.webp', '.tif'):
        p = os.path.join(RAW, f'{name}{ext}')
        if os.path.isfile(p):
            return Image.open(p).convert('RGB')
    raise FileNotFoundError(name)


def arr(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def to_linear(a):
    return np.power(np.clip(a, 0, 1), 2.2)


def to_srgb(a):
    return np.power(np.clip(a, 0, 1), 1 / 2.2)


def sample(src, u, v, wrap_x=False):
    """Bilinear sample of an HxWx3 array at float pixel coords (clamped, or wrapped in x)."""
    h, w = src.shape[:2]
    u = np.mod(u, w) if wrap_x else np.clip(u, 0, w - 1.001)
    v = np.clip(v, 0, h - 1.001)
    x0 = np.floor(u).astype(np.int32)
    y0 = np.floor(v).astype(np.int32)
    x1 = (x0 + 1) % w if wrap_x else np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    fx = (u - x0)[..., None]
    fy = (v - y0)[..., None]
    top = src[y0, x0] * (1 - fx) + src[y0, x1] * fx
    bot = src[y1, x0] * (1 - fx) + src[y1, x1] * fx
    return top * (1 - fy) + bot * fy


def fbm(octaves=6, base=6, seed=0, persistence=0.55):
    """Fractal noise over the canvas, 0..1."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((EH, EW), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        grid = rng.random((max(2, int(n * EH / EW)), n)).astype(np.float32)
        up = np.asarray(Image.fromarray((grid * 255).astype(np.uint8)).resize((EW, EH), Image.BICUBIC), np.float32) / 255
        acc += up * amp
        total += amp
        amp *= persistence
    acc /= total
    return (acc - acc.min()) / (acc.max() - acc.min() + 1e-6)


def stars(density=1.0, seed=1):
    rng = np.random.default_rng(seed)
    img = np.zeros((EH, EW, 3), np.float32)
    n = int(5200 * density)
    x = rng.integers(0, EW, n)
    y = rng.integers(0, EH, n)
    b = rng.pareto(2.6, n) * 0.16 + 0.04
    tint = rng.choice([[1, 1, 1], [1, 0.92, 0.82], [0.85, 0.9, 1]], n)
    img[y, x] = np.clip(b[:, None], 0, 3) * tint
    soft = np.asarray(Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.3)), np.float32) / 255
    return np.clip(img * 0.55 + soft * 2.2, 0, 1)


def paper(color, grain=0.035, seed=3):
    n = fbm(5, 40, seed) - 0.5
    fine = (RNG.random((EH, EW)).astype(np.float32) - 0.5)
    return np.clip(np.array(color, np.float32)[None, None] / 255 * (1 + n[..., None] * grain * 3 + fine[..., None] * grain), 0, 1)


def ink_for(rgb):
    """Judge the band just above the arc, where the words sit."""
    band = rgb[MT + TOP - 520:MT + TOP - 40, int(CX - 900):int(CX + 900)]
    lum = float((band @ np.array([0.2126, 0.7152, 0.0722], np.float32)).mean())
    return ('dark' if lum > 0.56 else 'light'), lum


def save(out_dir, name, rgb):
    rgb = np.clip(rgb, 0, 1)
    Image.fromarray((rgb * 255 + 0.5).astype(np.uint8)).save(os.path.join(out_dir, f'{name}.jpg'), quality=90, subsampling=0)
    return ink_for(rgb)


# ----------------------------------------------------------------------------- shot types
def bend(src, horizon, xc=0.5, rot=0.0, zoom=1.0, paste=None, clear_above=None, **_):
    """Wrap a landscape round the arc: its horizon row becomes the circle, like a tiny planet."""
    img = load(src)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=False)
    a = arr(img)
    sh, sw = a.shape[:2]
    arc_len = 2 * R * math.asin(min(1.0, CX / R)) * 1.02
    s = max(arc_len / sw, 1536 / (horizon * sh), 870 / ((1 - horizon) * sh)) * zoom
    out = sample(a, sw * xc + THETA * R / s, horizon * sh + (R - RAD) / s)
    if clear_above is not None:
        out[:MT + int(clear_above)] = 0
    if paste:
        # Lift a cut-out (e.g. the Earth in Earthrise) and set it just above the arc.
        cx, cy, half = paste['cx'], paste['cy'], paste['half']
        patch = img.crop((cx - half, cy - half, cx + half, cy + half))
        size = int(2 * half * s * paste.get('scale', 1.0))
        patch = arr(patch.resize((size, size), Image.LANCZOS))
        px = int(CX + paste.get('x', 0) - size / 2)
        py = int(MT + TOP + paste.get('y', -600) - size / 2)
        y0, x0 = max(py, 0), max(px, 0)
        y1, x1 = min(py + size, EH), min(px + size, EW)
        region = out[y0:y1, x0:x1]
        out[y0:y1, x0:x1] = np.maximum(region, patch[y0 - py:y1 - py, x0 - px:x1 - px])
    return out


def find_disc(src, thr):
    lum = arr(load(src)).mean(axis=2)
    m = lum > thr
    yy, xx = np.nonzero(m)
    return float(xx.mean()), float(yy.mean()), math.sqrt(m.sum() / math.pi)


def disc(src, circle='auto', thr=0.2, rot=0.0, bg=None, **_):
    """A photo of something round, scaled so its rim lands exactly on the arc.
    circle: [cx, cy, r] in source pixels, or 'auto' (bright object on a dark background, threshold thr)."""
    cx, cy, r = find_disc(src, thr) if circle == 'auto' else circle
    a = arr(load(src))
    k = r / R
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    x, y = (xs - CX) * k, (ys - CY) * k
    out = sample(a, cx + x * c - y * s_, cy + x * s_ + y * c)
    if bg is not None:
        back = paper(bg, 0.03) * (1 - 0.3 * np.exp(-np.clip(RAD - R, 0, None) / 70))[..., None]
        out = back * (1 - EDGE) + out * EDGE
    return out


def sphere(src, top_lat, lon0, light, albedo=1.0, atmo=None, atmo_w=60, night=None, ambient=0.02, spin=0.0, star_density=1.0, **_):
    """Orthographic render of an equirectangular map; the arc is the planet's limb.
    top_lat: latitude at the top of the limb (0 = bands run parallel to the arc)."""
    tex = to_linear(arr(load(src)))
    th, tw = tex.shape[:2]
    nx, ny = DX / R, DY / R
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    a = math.radians(90 - top_lat)
    y2 = ny * math.cos(a) - nz * math.sin(a)
    z2 = ny * math.sin(a) + nz * math.cos(a)
    nxs = nx
    if spin:
        cs, sn = math.cos(math.radians(spin)), math.sin(math.radians(spin))
        nxs, y2 = nx * cs - y2 * sn, nx * sn + y2 * cs
    lat = np.arcsin(np.clip(y2, -1, 1))
    lon = np.arctan2(nxs, z2) + math.radians(lon0)
    u = (lon / (2 * math.pi) + 0.5) * tw
    v = (0.5 - lat / math.pi) * th
    col = sample(tex, u, v, wrap_x=True) * albedo
    L = np.array(light, np.float32)
    L /= np.linalg.norm(L)
    ndl = nx * L[0] + ny * L[1] + nz * L[2]
    lit = col * (ambient + 1.15 * np.clip(ndl, 0, 1)[..., None] ** 0.9)
    if night:
        nt = to_linear(arr(load(night)))
        lights = sample(nt, u * nt.shape[1] / tw, v * nt.shape[0] / th, wrap_x=True)
        dark = np.clip(-ndl * 4 + 0.3, 0, 1)[..., None]
        lit += np.clip(lights[..., :1] - 0.01, 0, 1) * np.array([1.0, 0.72, 0.4]) * 1.6 * dark
    out = to_linear(stars(star_density, 2))
    if atmo is not None:
        ac = np.array(atmo, np.float32)
        limb_lit = np.clip((DX * L[0] + DY * L[1]) / (RAD + 1e-6) * 0.8 + 0.45, 0, 1)
        glow = np.exp(-np.clip(RAD - R, 0, None) / atmo_w) * (RAD >= R) * limb_lit
        out = out + glow[..., None] * ac
        lit = lit + ((1 - nz) ** 3 * np.clip(ndl + 0.25, 0, 1))[..., None] * ac * 0.8
    out = out * (1 - EDGE) + lit * EDGE
    return to_srgb(out)


def texture(src, bg, fit=1.0, xc=0.5, yc=0.5, rim=0.5, shade=0.35, **_):
    """Pour a texture (a field, a plate, a wall of ice) into the disc, as if it were a round object."""
    a = arr(load(src))
    sh, sw = a.shape[:2]
    s = max(EW / sw, (EH - MT - TOP) / sh) * fit
    tex = sample(a, sw * xc + (xs - CX) / s, sh * yc + (ys - (MT + TOP + (EH - MT - TOP) / 2)) / s)
    depth = np.clip((R - RAD) / 900, 0, 1)[..., None]
    tex = tex * (1 - shade * depth ** 0.7)
    tex += np.exp(-np.clip(R - RAD, 0, None) / 10)[..., None] * rim * 0.6
    shadow = 1 - 0.38 * np.exp(-np.clip(RAD - R, 0, None) / 90)[..., None]
    return paper(bg, 0.03) * shadow * (1 - EDGE) + tex * EDGE


# ----------------------------------------------------------------------------- procedural
def draw_layer(fn, blur=0.0):
    im = Image.new('L', (EW, EH), 0)
    fn(ImageDraw.Draw(im))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255


def arc_pts(r, t0, t1, n=600):
    t = np.linspace(t0, t1, n)
    return list(zip(CX + r * np.sin(t), CY - r * np.cos(t)))


def blueprint(color=(44, 96, 150), **_):
    bg = paper(color, 0.05, seed=11)

    def lines(d):
        d.line(arc_pts(R, -0.75, 0.75), fill=255, width=16)
        d.line(arc_pts(R - 95, -0.75, 0.75), fill=200, width=7)
        d.line(arc_pts(R - 470, -0.75, 0.75), fill=190, width=7)
        d.line(arc_pts(R + 420, -0.75, 0.75), fill=110, width=5)
        for t in np.arange(-0.7, 0.71, 0.055):
            d.line([(CX + (R - 470) * math.sin(t), CY - (R - 470) * math.cos(t)), (CX + R * math.sin(t), CY - R * math.cos(t))], fill=215, width=8)
        for t in np.arange(-0.7, 0.71, 0.011):
            ln = 70 if abs(round(t / 0.011)) % 5 == 0 else 34
            d.line([(CX + R * math.sin(t), CY - R * math.cos(t)), (CX + (R + ln) * math.sin(t), CY - (R + ln) * math.cos(t))], fill=230, width=5)
        for k in range(7):
            x0 = 520 + k * 46
            d.line([(x0, 380), (x0 + 520, 1120)], fill=235, width=9)
            d.line([(EW - x0, 300), (EW - x0 - 560, 1060)], fill=225, width=9)
        for k in range(4):
            d.line([(1300 + k * 34, 120), (1300 + k * 34, 900)], fill=200, width=6)
        d.line([(2400, 140), (3700, 1200)], fill=210, width=8)
        d.line([(3900, 260), (2900, 1300)], fill=180, width=6)
        d.ellipse([CX - 120, MT + TOP - 760, CX + 120, MT + TOP - 520], outline=200, width=7)
    mask = draw_layer(lines, 1.6)
    chalk = np.clip(fbm(4, 300, 5) * 1.6 - 0.15 + RNG.random((EH, EW)).astype(np.float32) * 0.5, 0, 1)
    m = (mask * chalk)[..., None]
    return bg * (1 - m * 0.9) + np.array([0.95, 0.97, 1.0]) * m * 0.95


def globe(color=(243, 237, 224), **_):
    bg = paper(color, 0.03, seed=13)
    tilt, roll = math.radians(58), math.radians(-14)

    def project(lat, lon):
        x = np.cos(lat) * np.sin(lon)
        y = np.sin(lat)
        z = np.cos(lat) * np.cos(lon)
        y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
        x, y = x * math.cos(roll) - y * math.sin(roll), x * math.sin(roll) + y * math.cos(roll)
        return x, y, z

    def polyline(d, lat, lon, width):
        x, y, z = project(lat, lon)
        pts = list(zip(CX + x * R, CY - y * R))
        for i in range(len(pts) - 1):
            if z[i] > 0 and z[i + 1] > 0:
                d.line([pts[i], pts[i + 1]], fill=255, width=width)

    t = np.linspace(0, 2 * math.pi, 1400)
    mer = lambda lo: (np.linspace(-math.pi / 2, math.pi / 2, 900), np.full(900, math.radians(lo)))

    def ink(d):
        for la in range(-80, 81, 10):
            polyline(d, np.full_like(t, math.radians(la)), t, 5)
        for lo in range(0, 360, 10):
            polyline(d, *mer(lo), 5)
        d.line(arc_pts(R, -0.8, 0.8, 900), fill=255, width=12)

    def red(d):
        for lo in (20, 80, 150):
            polyline(d, *mer(lo), 11)
        polyline(d, np.full_like(t, math.radians(23.4)), t, 9)

    def blue(d):
        for lo in (50, 110, 200):
            polyline(d, *mer(lo), 11)
        polyline(d, np.full_like(t, 0.0), t, 9)

    out = bg * (1 - EDGE * 0.04)
    for fn, col, k in ((ink, (0.16, 0.15, 0.14), 0.8), (red, (0.84, 0.18, 0.2), 1.0), (blue, (0.17, 0.42, 0.85), 1.0)):
        m = draw_layer(fn, 1.0)[..., None] * k
        out = out * (1 - m) + np.array(col) * m
    return out


def collage(color=(238, 231, 214), base=(36, 70, 158), seed=21, **_):
    rng = np.random.default_rng(seed)
    out = paper(color, 0.035, seed=17) * (1 - EDGE) + paper(base, 0.06, seed=19) * EDGE
    palette = [(205, 45, 42), (247, 205, 70), (38, 140, 92), (241, 125, 45), (234, 150, 178), (92, 42, 30), (250, 246, 236), (20, 24, 28)]
    for k in range(34):
        cx = rng.uniform(CX - 2300, CX + 2300)
        cy = rng.uniform(MT + TOP - 60, EH + 200)
        rad = rng.uniform(140, 520)
        n = rng.integers(5, 11)
        ang = np.sort(rng.uniform(0, 2 * math.pi, n))
        rr = rad * rng.uniform(0.55, 1.25, n)
        pts = list(zip(cx + rr * np.cos(ang), cy + rr * np.sin(ang)))
        circle = k % 9 == 4

        def shape(d, ox=0, oy=0):
            if circle:
                d.ellipse([cx - rad + ox, cy - rad + oy, cx + rad + ox, cy + rad + oy], fill=255)
            else:
                d.polygon([(x + ox, y + oy) for x, y in pts], fill=255)
        sh = draw_layer(lambda d: shape(d, 18, 22), 10)[..., None]
        m = draw_layer(shape, 0.8)[..., None]
        out = out * (1 - sh * EDGE * 0.35)
        out = out * (1 - m * EDGE) + paper(palette[k % len(palette)], 0.07, seed=30 + k) * m * EDGE
    return out


def topo(**_):
    n = fbm(7, 5, 23, 0.52)
    line = np.clip(1 - np.abs(np.mod(n * 26, 1.0) - 0.5) / 0.06, 0, 1) ** 2
    major = np.clip(1 - np.abs(np.mod(n * 26 / 5, 1.0) - 0.5) / 0.018, 0, 1)
    land = np.array([0.05, 0.12, 0.1]) * (0.6 + 0.8 * n[..., None])
    d = land + line[..., None] * np.array([0.86, 0.7, 0.36]) * 0.75 + major[..., None] * np.array([1.0, 0.85, 0.5]) * 0.9
    grid = (np.abs(np.mod(xs, 240) - 120) > 118) | (np.abs(np.mod(ys, 240) - 120) > 118)
    bg = paper((14, 18, 26), 0.06, seed=29) + grid[..., None] * 0.035
    bg = bg + np.exp(-np.clip(RAD - R, 0, None) / 40)[..., None] * np.array([0.9, 0.7, 0.35]) * 0.5
    return bg * (1 - EDGE) + d * EDGE


def thin_film(**_):
    n1, n2, n3 = fbm(6, 4, 31), fbm(6, 4, 37), fbm(5, 3, 41)
    swirl = sample(np.repeat(n3[..., None], 3, axis=2), xs + (n1 - 0.5) * 2600, ys + (n2 - 0.5) * 2600)[..., 0]
    t = swirl * 3.2 + (R - RAD) / 2400
    film = (0.5 + 0.5 * np.cos(2 * math.pi * (t[..., None] + np.array([0.0, 0.33, 0.67])))) ** 1.4 * 1.05
    rim = np.exp(-np.clip(R - RAD, 0, None) / 30)[..., None]
    d = film * (0.75 + 0.25 * rim) + rim * 0.5
    bg = stars(0.35, 43) * 0.6 + np.exp(-np.clip(RAD - R, 0, None) / 160)[..., None] * np.array([0.5, 0.2, 0.7]) * 0.35
    return bg * (1 - EDGE) + d * EDGE


PROCEDURAL = {'blueprint': blueprint, 'globe': globe, 'collage': collage, 'topo': topo, 'thin_film': thin_film}


def earth_rise(night='earth_night', top_lat=52, lon0=60, **_):
    """Opening/ending: Earth's night side, and (separately) the sunrise glow along the limb."""
    base = sphere(night, top_lat, lon0, (0.0, 0.25, -1.0), albedo=0.4, ambient=0.0)
    h = RAD - R
    ang = np.exp(-(THETA / 0.42) ** 2) * 0.85 + 0.15
    above = (h >= 0)[..., None]
    hh = np.clip(h, 0, None)[..., None]
    glow = (np.exp(-hh / 16) * np.array([1.0, 0.42, 0.1]) * 2.6 + np.exp(-hh / 70) * np.array([1.0, 0.62, 0.3]) * 0.6
            + np.exp(-hh / 230) * np.array([0.22, 0.5, 1.0]) * 0.85 + np.exp(-hh / 700) * np.array([0.08, 0.2, 0.55]) * 0.35) * above
    inner = np.exp(-np.clip(-h, 0, None) / 22)[..., None] * np.array([1.0, 0.5, 0.2]) * 0.8 * (~(h >= 0))[..., None]
    g = (glow + inner) * ang[..., None]
    return base, to_srgb(g / (1 + g) * 1.35)


# ----------------------------------------------------------------------------- main
def build(entry):
    kind = entry['type']
    p = {k: v for k, v in entry.items() if k not in ('name', 'type', 'credit', 'license', 'url', 'note')}
    if kind == 'bend':
        return bend(**p)
    if kind == 'disc':
        return disc(**p)
    if kind == 'sphere':
        return sphere(**p)
    if kind == 'texture':
        return texture(**p)
    if kind == 'procedural':
        return PROCEDURAL[p.pop('kind')](**p)
    raise ValueError(f'unknown shot type {kind}')


def main():
    global RAW
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--raw', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    RAW = a.raw
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.manifest)), exist_ok=True)
    only = set(filter(None, a.only.split(',')))
    shots = json.load(open(a.config))
    manifest = json.load(open(a.manifest)) if os.path.exists(a.manifest) else {}
    for entry in shots:
        name = entry['name']
        if only and name not in only:
            continue
        try:
            if entry['type'] == 'earth_rise':
                base, glow = earth_rise(**{k: v for k, v in entry.items() if k not in ('name', 'type', 'credit', 'license', 'url')})
                ink, lum = save(a.out, name, base)
                save(a.out, f'{name}_glow', glow)
            else:
                ink, lum = save(a.out, name, build(entry))
            manifest[name] = {'ink': entry.get('ink', ink), 'lum': round(lum, 3), 'type': entry['type']}
            print(f'{name:18s} {entry["type"]:10s} lum={lum:.2f} ink={manifest[name]["ink"]}', flush=True)
        except FileNotFoundError as e:
            print(f'{name:18s} SKIPPED - missing source image {e}', flush=True)
    json.dump(manifest, open(a.manifest, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
