#!/usr/bin/env python3
"""Put product photos on the warm Mazo Moon backdrop used by the v2 images.
Usage: python3 tools/backdrop.py in.jpg out.jpg"""
import sys
from PIL import Image, ImageFilter, ImageDraw, ImageChops
import numpy as np
from collections import deque

S = 800
TOP, BOTTOM = (236, 231, 225), (222, 215, 207)


def backdrop():
    y = np.linspace(0, 1, S)[:, None]
    x = np.linspace(0, 1, S)[None, :]
    t = np.clip(0.65 * y + 0.35 * x, 0, 1)[..., None]
    arr = np.array(TOP) * (1 - t) + np.array(BOTTOM) * t
    # soft light from the top left
    r = np.sqrt((x - .25) ** 2 + (y - .15) ** 2)[..., None]
    arr = arr + 10 * np.clip(1 - r / .8, 0, 1)
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def bg_mask(im, tol=16):
    a = np.asarray(im.convert('RGB')).astype(int)
    h, w, _ = a.shape
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    ref = np.median(edge, axis=0)
    near = (np.abs(a - ref).max(axis=2) <= tol) & (a.mean(axis=2) > 200)
    seen = np.zeros((h, w), bool)
    q = deque()
    for xx in range(w):
        for yy in (0, h - 1):
            if near[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; q.append((yy, xx))
    for yy in range(h):
        for xx in (0, w - 1):
            if near[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; q.append((yy, xx))
    while q:
        yy, xx = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = yy + dy, xx + dx
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and near[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    return seen, ref


def framed(src, dst, scale=.8):
    """For lifestyle photos: a rounded photo card resting on the backdrop."""
    im = Image.open(src).convert('RGB')
    base = backdrop(); n = int(S * scale); off = ((S - n) // 2, (S - n) // 2 - 4)
    sub = im.resize((n, n), Image.LANCZOS)
    m = Image.new('L', (n, n), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, n - 1, n - 1), 22, fill=255)
    sh = Image.new('L', (S, S), 0); sh.paste(m, (off[0] + 4, off[1] + 18))
    sh = sh.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * .30))
    base = Image.composite(Image.new('RGB', (S, S), (120, 104, 92)), base, sh)
    base.paste(sub, off, m.filter(ImageFilter.GaussianBlur(.6)))
    base.save(dst, quality=88)


def main(src, dst, scale=.86):
    im = Image.open(src).convert('RGB').resize((S, S), Image.LANCZOS)
    bgm, ref = bg_mask(im)
    fg = Image.fromarray((~bgm * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    # shift the photo's own light grey towards the warm backdrop so edges blend
    warm = Image.new('RGB', (S, S), TOP)
    tinted = ImageChops.multiply(im, Image.new('RGB', (S, S), (252, 248, 242)))
    base = backdrop()
    n = int(S * scale); off = ((S - n) // 2, (S - n) // 2 + 6)
    sub = tinted.resize((n, n), Image.LANCZOS); m = fg.resize((n, n), Image.LANCZOS)
    sh = Image.new('L', (S, S), 0); sh.paste(m, (off[0] + 6, off[1] + 16))
    sh = sh.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * .32))
    dark = Image.new('RGB', (S, S), (120, 104, 92))
    base = Image.composite(dark, base, sh)
    base.paste(sub, off, m)
    base.save(dst, quality=88)


if __name__ == '__main__':
    (framed if '--frame' in sys.argv else main)(sys.argv[1], sys.argv[2])
