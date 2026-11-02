#!/usr/bin/env python3
"""Build the vanilla reference shelf for the HOI4 asset skill from an installed game (read-only).

Usage:
  py.sh build_shelf.py --game "<HOI4 install dir>" --out <dir> --families-json families.json [--only id,id] [--seed 0]

Writes under --out:
  vanilla_reference/<family folder>/<texture stem>.png   (RGBA, native size)
  vanilla_reference/<family folder>/contact_sheet.png
  catalog.json                                           (provenance for every family)
  skipped_all.json                                       (every skipped file with its reason)

Method (deterministic; same game files + same families.json + same --seed give the same shelf):
  1. Candidates: textures under each family's folders/patterns (base game + dlc/* + integrated_dlc/*, a later root
     overrides the same relative path), optionally restricted by a classification (idea category from common/ideas,
     character portrait block and role from common/characters, advisor idea_token), and by the family's accepted canvas.
  2. Exclusions: undecodable or unsupported DDS formats, all-transparent / near-empty images, uniform images, placeholder
     names, and duplicate pixel content (first by path wins). Every exclusion is recorded with a reason.
  3. Descriptor per candidate (19 numbers): mean/std of Lab L,a,b over visible pixels; Sobel edge density of the image
     composited on grey; alpha coverage and semi-transparent fraction; 6-bin hue histogram (chroma weighted), neutral
     fraction and 3 lightness bins. Standardised per family (z-score).
  4. k-medoids (PAM style, k-medoids++ init with a fixed seed, k = family k, default 15) on the descriptors. Each
     medoid is a style representative; the medoids together span the range of the family.
  5. Spread: inside each cluster the pick is the member nearest the medoid that satisfies (a) a base-game/DLC quota
     proportional to the candidate pool (forced onto the clusters whose medoid is closest to a DLC member) and (b) a per
     nation cap, where the nation is the country tag found in the folder or file name (families with no hint use none).
  6. Decode to PNG (RGBA native size, file name = texture stem) and write a labelled contact sheet.
"""
import argparse
import collections
import datetime
import hashlib
import json
import math
import os
import re
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

BS = chr(92)
TEX_EXT = ('.dds', '.tga', '.png')
PLACEHOLDER_RE = re.compile(r'(^|[_\-\s])(test|placeholder|dummy|temp|tmp|todo|empty|missing|unused|backup|copy|wip)([_\-\s\d]|$)', re.I)


# ----------------------------------------------------------------------------
# game roots, sprite index, classification sources
# ----------------------------------------------------------------------------
class Game:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.roots = [('base', self.path)]
        for sub in ('dlc', 'integrated_dlc'):
            d = os.path.join(self.path, sub)
            if os.path.isdir(d):
                for n in sorted(os.listdir(d)):
                    if os.path.isdir(os.path.join(d, n)):
                        self.roots.append((sub + '/' + n, os.path.join(d, n)))
        self.rp = dict(self.roots)
        self._sprites = None
        self._tags = None

    def rel(self, p):
        return os.path.relpath(p, self.path).replace(BS, '/')

    def group(self, rootname):
        return 'base' if rootname == 'base' else 'dlc'

    def version(self):
        d = {}
        try:
            d = json.load(open(os.path.join(self.path, 'launcher-settings.json'), encoding='utf-8-sig'))
        except (OSError, ValueError):
            pass
        exe = os.path.join(self.path, 'hoi4.exe')
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(exe)).isoformat(timespec='seconds') if os.path.exists(exe) else None
        return d.get('version'), d.get('rawVersion'), mt

    def textures(self, specs):
        """Map normalised relative path -> (rootname, abspath, relpath-to-game). Later roots override earlier ones."""
        out = {}
        overridden = 0
        for spec in specs:
            nonrec = spec.startswith('=')
            spec = spec.lstrip('=')
            rel, _, pat = spec.partition('::')
            rx = re.compile(pat, re.I) if pat else None
            for rn, rp in self.roots:
                base = os.path.join(rp, rel.replace('/', os.sep))
                if not os.path.isdir(base):
                    continue
                for dp, dn, fn in os.walk(base):
                    if nonrec:
                        dn[:] = []
                    dn.sort()
                    for f in sorted(fn):
                        if not f.lower().endswith(TEX_EXT):
                            continue
                        if rx and not rx.search(f):
                            continue
                        p = os.path.join(dp, f)
                        r = os.path.relpath(p, rp).replace(BS, '/')
                        k = norm(r)
                        if k in out and out[k][0] != rn:
                            overridden += 1
                        out[k] = (rn, p, self.rel(p))
        return out

    def resolve(self, rel, prefer=None):
        rel = norm(rel)
        if not rel:
            return None
        order = ([prefer] if prefer else []) + [r for r, _ in self.roots]
        for rn in order:
            p = os.path.join(self.rp[rn], rel.replace('/', os.sep))
            if os.path.exists(p):
                return p
        return None

    def txt_files(self, reldir):
        out = []
        for _rn, rp in self.roots:
            d = os.path.join(rp, reldir.replace('/', os.sep))
            if os.path.isdir(d):
                for dp, dn, fn in os.walk(d):
                    dn.sort()
                    for f in sorted(fn):
                        if f.endswith('.txt'):
                            out.append(os.path.join(dp, f))
        return out

    def sprites(self):
        if self._sprites is None:
            res = []
            for rn, rp in self.roots:
                for dp, dn, fn in os.walk(rp):
                    if rn == 'base' and dp == rp:
                        dn[:] = [x for x in dn if x not in ('dlc', 'integrated_dlc')]
                    for f in fn:
                        if f.endswith('.gfx'):
                            p = os.path.join(dp, f)
                            try:
                                txt = open(p, encoding='utf-8-sig', errors='replace').read()
                            except OSError:
                                continue
                            for _typ, body, _raw in blocks(txt):
                                a = top_attrs(body)
                                if 'name' in a and a.get('texturefile'):
                                    res.append(dict(root=rn, file=os.path.relpath(p, rp).replace(BS, '/'), name=a['name'],
                                                    tex=norm(a['texturefile']), frames=a.get('noofframes', '1')))
            self._sprites = res
        return self._sprites

    def sprite_by_name(self):
        d = {}
        for s in self.sprites():
            d.setdefault(s['name'].lower(), s)
        return d

    def sprites_by_tex(self):
        d = collections.defaultdict(list)
        for s in self.sprites():
            d[s['tex']].append(s)
        return d

    def tags(self):
        if self._tags is None:
            t = set()
            for p in self.txt_files('common/country_tags'):
                for line in open(p, encoding='utf-8-sig', errors='replace'):
                    m = re.match(r'\s*([A-Z0-9]{3})\s*=', line)
                    if m:
                        t.add(m.group(1))
            self._tags = t
        return self._tags


def norm(t):
    t = t.replace(BS, '/').lower()
    t = re.sub(r'/+', '/', t).lstrip('/')
    return t


def strip_comments(t):
    out = []
    for line in t.split('\n'):
        res = []
        q = False
        for ch in line:
            if ch == '"':
                q = not q
            if ch == '#' and not q:
                break
            res.append(ch)
        out.append(''.join(res))
    return '\n'.join(out)


def blocks(text):
    t = strip_comments(text)
    pos = 0
    for m in re.finditer(r'(\w+)\s*=\s*\{', t):
        if m.start() < pos:
            continue
        typ = m.group(1)
        if typ.lower() == 'spritetypes':
            continue
        depth = 1
        i = m.end()
        while i < len(t) and depth:
            c = t[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            i += 1
        pos = i
        yield typ, t[m.end():i - 1], t[m.start():i]


def top_attrs(body):
    d = {}
    s = ''
    depth = 0
    for c in body:
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif depth == 0:
            s += c
    for m in re.finditer(r'(\w+)\s*=\s*("[^"]*"|[^\s{}]+)', s):
        d.setdefault(m.group(1).lower(), m.group(2).strip('"'))
    return d


def idea_textures(game):
    """norm texture path -> set of idea categories (common/ideas) that use it."""
    by_name = game.sprite_by_name()
    res = collections.defaultdict(set)
    for p in game.txt_files('common/ideas'):
        txt = open(p, encoding='utf-8-sig', errors='replace').read()
        for typ, body, _raw in blocks(txt):
            if typ != 'ideas':
                continue
            for cat, cbody, _craw in blocks(body):
                for _idea, ibody, _iraw in blocks(cbody):
                    pic = top_attrs(ibody).get('picture')
                    if not pic:
                        continue
                    for cand in ([pic] if pic.startswith('GFX_') else ['GFX_idea_' + pic]):
                        s = by_name.get(cand.lower())
                        if s:
                            res[s['tex']].add(cat)
                            break
    return res


def character_textures(game):
    """norm texture path -> dict(kinds=set of 'leader','commander','operative','scientist','advisor_card')."""
    by_name = game.sprite_by_name()
    res = collections.defaultdict(set)
    role_re = {
        'country_leader': re.compile(r'\bcountry_leader\s*='),
        'commander': re.compile(r'\b(corps_commander|field_marshal|navy_leader)\s*='),
        'operative': re.compile(r'\boperative\s*='),
        'scientist': re.compile(r'\bscientist\s*='),
    }
    for p in game.txt_files('common/characters'):
        txt = open(p, encoding='utf-8-sig', errors='replace').read()
        for typ, body, _raw in blocks(txt):
            if typ != 'characters':
                continue
            for _cname, cbody, _craw in blocks(body):
                clean = strip_comments(cbody)
                roles = {k for k, rx in role_re.items() if rx.search(clean)}
                portraits = {}
                for t2, b2, _r2 in blocks(cbody):
                    if t2 == 'portraits':
                        for t3, b3, _r3 in blocks(b2):
                            portraits[t3.lower()] = top_attrs(b3)
                for blk, a in portraits.items():
                    for key in ('large', 'small'):
                        v = a.get(key)
                        s = by_name.get(v.lower()) if v else None
                        if not s:
                            continue
                        if key == 'large':
                            if 'operative' in roles:
                                res[s['tex']].add('operative')
                            elif 'scientist' in roles:
                                res[s['tex']].add('scientist')
                            elif blk in ('army', 'navy') and 'commander' in roles:
                                res[s['tex']].add('commander')
                            elif blk == 'civilian' and 'country_leader' in roles:
                                res[s['tex']].add('leader')
                            elif blk == 'civilian':
                                res[s['tex']].add('civilian_other')
                            else:
                                res[s['tex']].add('commander_other')
                for m in re.finditer(r'idea_token\s*=\s*"?([A-Za-z0-9_\-\.]+)"?', clean):
                    s = by_name.get('gfx_idea_' + m.group(1).lower())
                    if s:
                        res[s['tex']].add('advisor_card')
    return res


# ----------------------------------------------------------------------------
# headers and decoding
# ----------------------------------------------------------------------------
class Unsupported(Exception):
    pass


def dds_header(h):
    (size, flags, height, width, pitch, depth, mips) = struct.unpack('<7I', h[4:32])
    pfflags, fourcc = struct.unpack('<I4s', h[80:88])
    rgbbits, rm, gm, bm, am = struct.unpack('<5I', h[88:108])
    dxgi = struct.unpack('<I', h[128:132])[0] if (pfflags & 4 and fourcc == b'DX10' and len(h) >= 132) else None
    return dict(w=width, h=height, mips=max(mips, 1), pfflags=pfflags, fourcc=fourcc.decode('latin1').strip('\0'),
                bits=rgbbits, masks=(rm, gm, bm, am), dxgi=dxgi)


def header(path):
    """(w, h) or None."""
    e = os.path.splitext(path)[1].lower()
    try:
        with open(path, 'rb') as f:
            h = f.read(148)
        if e == '.dds' and h[:4] == b'DDS ':
            d = dds_header(h)
            return d['w'], d['h']
        if e == '.tga':
            w, hh = struct.unpack('<HH', h[12:16])
            return w, hh
        if e == '.png' and h[:8] == b'\x89PNG\r\n\x1a\n':
            w, hh = struct.unpack('>II', h[16:24])
            return w, hh
    except (OSError, ValueError, struct.error):
        return None
    return None


def _channel(px, mask):
    if not mask:
        return None
    shift = (mask & -mask).bit_length() - 1
    bits = bin(mask).count('1')
    v = (px & mask) >> shift
    if bits == 8:
        return v.astype(np.uint8)
    return ((v.astype(np.uint32) * 255 + ((1 << bits) - 1) // 2) // ((1 << bits) - 1)).astype(np.uint8)


def decode(path):
    """-> (PIL RGBA image, format description). Raises Unsupported or other exceptions on failure."""
    e = os.path.splitext(path)[1].lower()
    if e == '.dds':
        data = open(path, 'rb').read()
        d = dds_header(data[:148])
        if d['dxgi'] is not None:
            raise Unsupported('DDS DX10 DXGI %d is not decodable by Pillow' % d['dxgi'])
        if d['pfflags'] & 4:  # FourCC compressed
            im = Image.open(path)
            im.load()
            return im.convert('RGBA'), 'DDS ' + d['fourcc']
        w, h, bits = d['w'], d['h'], d['bits']
        rm, gm, bm, am = d['masks']
        off = 128
        if bits == 32:
            px = np.frombuffer(data, dtype='<u4', count=w * h, offset=off).reshape(h, w)
        elif bits == 16:
            px = np.frombuffer(data, dtype='<u2', count=w * h, offset=off).reshape(h, w).astype(np.uint32)
        elif bits == 24:
            raw = np.frombuffer(data, dtype=np.uint8, count=w * h * 3, offset=off).reshape(h, w, 3).astype(np.uint32)
            px = raw[..., 0] | (raw[..., 1] << 8) | (raw[..., 2] << 16)
        else:
            raise Unsupported('uncompressed DDS with %d bits' % bits)
        px = px.astype(np.uint32)
        out = np.zeros((h, w, 4), np.uint8)
        out[..., 0] = _channel(px, rm)
        out[..., 1] = _channel(px, gm)
        out[..., 2] = _channel(px, bm)
        a = _channel(px, am)
        out[..., 3] = a if a is not None else 255
        return Image.fromarray(out, 'RGBA'), 'DDS uncompressed %dbpp masks=%x/%x/%x/%x' % (bits, rm, gm, bm, am)
    if e == '.tga':
        with open(path, 'rb') as f:
            hd = f.read(18)
        alphabits = hd[17] & 15
        im = Image.open(path)
        im.load()
        im = im.convert('RGBA')
        if alphabits == 0:
            arr = np.asarray(im).copy()
            arr[..., 3] = 255
            im = Image.fromarray(arr, 'RGBA')
        return im, 'TGA alphabits=%d' % alphabits
    im = Image.open(path)
    im.load()
    return im.convert('RGBA'), 'PNG'


# ----------------------------------------------------------------------------
# descriptors, k-medoids, selection
# ----------------------------------------------------------------------------
def rgb2lab(rgb):
    c = rgb.astype(np.float64) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ M.T
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16.0 / 116.0)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1)


def descriptor(rgba):
    arr = np.asarray(rgba).astype(np.float64)
    al = arr[..., 3] / 255.0
    vis = al > 0.06
    cov = float(vis.mean())
    semi = float(((al > 0.06) & (al < 0.94)).mean())
    lab = rgb2lab(arr[..., :3])
    sel = al > 0.5
    if sel.sum() < 4:
        sel = vis
    if sel.sum() == 0:
        return np.zeros(19)
    px = lab[sel]
    stats = list(px.mean(0)) + list(px.std(0))
    comp = arr[..., :3] * al[..., None] + 128.0 * (1 - al[..., None])
    Lc = rgb2lab(comp)[..., 0]
    gx = ndimage.sobel(Lc, axis=1, mode='nearest')
    gy = ndimage.sobel(Lc, axis=0, mode='nearest')
    edge = float(np.hypot(gx, gy).mean())
    chroma = np.hypot(px[:, 1], px[:, 2])
    hue = (np.degrees(np.arctan2(px[:, 2], px[:, 1])) + 360.0) % 360.0
    colored = chroma > 8
    hist = np.zeros(6)
    if colored.any():
        hb = np.minimum((hue[colored] // 60).astype(int), 5)
        np.add.at(hist, hb, chroma[colored])
        hist = hist / max(hist.sum(), 1e-9) * float(colored.mean())
    neutral = float((~colored).mean())
    Ls = px[:, 0]
    lb = [float((Ls < 35).mean()), float(((Ls >= 35) & (Ls < 65)).mean()), float((Ls >= 65).mean())]
    return np.array(stats + [edge, cov, semi] + list(hist) + [neutral] + lb)


def kmedoids(D, k, seed):
    n = len(D)
    rng = np.random.default_rng(seed)
    medoids = [int(np.argmin(D.sum(1)))]
    while len(medoids) < k:
        dmin = D[:, medoids].min(1) ** 2
        s = dmin.sum()
        if s <= 0:
            rest = [i for i in range(n) if i not in medoids]
            medoids.append(rest[0])
            continue
        medoids.append(int(rng.choice(n, p=dmin / s)))
    medoids = np.array(sorted(set(medoids)))
    labels = D[:, medoids].argmin(1)
    for _ in range(200):
        newm = []
        for ci in range(len(medoids)):
            idx = np.where(labels == ci)[0]
            if len(idx) == 0:
                newm.append(medoids[ci])
                continue
            sub = D[np.ix_(idx, idx)].sum(1)
            newm.append(int(idx[np.argmin(sub)]))
        newm = np.array(newm)
        newlabels = D[:, newm].argmin(1)
        if np.array_equal(newm, medoids) and np.array_equal(newlabels, labels):
            break
        medoids, labels = newm, newlabels
    return medoids, labels


def choose(items, X, k, seed, nation_cap):
    """items: list of dicts with group/nation. Returns (indices, info)."""
    n = len(items)
    if n <= k:
        return list(range(n)), dict(method='all candidates (fewer than k)', clusters=None)
    Z = (X - X.mean(0)) / np.where(X.std(0) < 1e-9, 1.0, X.std(0))
    D = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
    medoids, labels = kmedoids(D, k, seed)
    k = len(medoids)
    members = []
    for ci in range(k):
        idx = np.where(labels == ci)[0]
        idx = idx[np.argsort(D[idx, medoids[ci]], kind='stable')]
        members.append(list(idx))
    # base / dlc quota
    ndlc = sum(1 for it in items if it['group'] == 'dlc')
    forced = set()
    quota = 0
    if 0 < ndlc < n:
        frac = ndlc / n
        quota = min(ndlc, max(1 if frac >= 0.03 else 0, int(round(k * frac))), (k + 1) // 2)
        have = sum(1 for ci in range(k) if items[medoids[ci]]['group'] == 'dlc')
        need = quota - have
        if need > 0:
            opts = []
            for ci in range(k):
                if items[medoids[ci]]['group'] == 'dlc':
                    continue
                cand = [m for m in members[ci] if items[m]['group'] == 'dlc']
                if cand:
                    opts.append((D[cand[0], medoids[ci]], ci, cand[0]))
            opts.sort()
            for _, ci, _m in opts[:need]:
                forced.add(ci)
    picks = [None] * k
    counts = collections.Counter()
    order = sorted(range(k), key=lambda c: (-len(members[c]), c))
    for ci in order:
        pick = None
        for m in members[ci]:
            if ci in forced and items[m]['group'] != 'dlc':
                continue
            nat = items[m]['nation']
            if nation_cap and nat and counts[nat] >= nation_cap:
                continue
            pick = m
            break
        if pick is None:
            pick = int(medoids[ci])
        picks[ci] = pick
        if items[pick]['nation']:
            counts[items[pick]['nation']] += 1
    info = dict(method='k-medoids k=%d seed=%d on %d standardised descriptors' % (k, seed, X.shape[1]),
                dlc_quota=quota, forced_dlc_clusters=len(forced), nation_cap=nation_cap or None,
                cluster_sizes=[len(m) for m in members],
                medoid_changed=sum(1 for ci in range(k) if picks[ci] != medoids[ci]))
    out = sorted(set(picks), key=lambda i: items[i]['key'])
    for i, ci in zip(picks, range(k)):
        items[i]['cluster'] = ci
        items[i]['medoid'] = bool(i == medoids[ci])
    return out, info


# ----------------------------------------------------------------------------
# contact sheet
# ----------------------------------------------------------------------------
def font(size):
    try:
        return ImageFont.load_default(size=size)
    except (OSError, ValueError, TypeError):
        return ImageFont.load_default()


def checker(w, h, s=8):
    yy, xx = np.mgrid[0:h, 0:w]
    v = np.where(((yy // s) + (xx // s)) % 2 == 0, 196, 160).astype(np.uint8)
    return Image.fromarray(np.stack([v, v, v, np.full_like(v, 255)], -1), 'RGBA')


def wrap_label(draw, text, fnt, width):
    lines, cur = [], ''
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) > width and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    lines.append(cur)
    return lines


def contact_sheet(path, tiles, small_max=80, max_width=1500):
    """tiles: list of dict(img=PIL RGBA, label=str, sub=str)."""
    fnt = font(11)
    dummy = ImageDraw.Draw(Image.new('RGB', (4, 4)))
    cells = []
    for t in tiles:
        im = t['img']
        w, h = im.size
        content = [(im, 1)]
        cw, ch = w, h
        if max(w, h) <= small_max:
            cw, ch = w + 8 + 2 * w, 2 * h
            content = [(im, 1), (im.resize((2 * w, 2 * h), Image.NEAREST), 2)]
        cw = max(cw, 150) + 8
        ch = ch + 8
        lines = wrap_label(dummy, t['label'], fnt, cw - 8)[:3]
        cells.append((t, content, cw, ch, lines))
    cell_w = [c[2] for c in cells]
    pad = 6
    cols = 1
    while cols < len(cells):
        rows_w = [sum(cell_w[i:i + cols + 1]) + pad * (cols + 2) for i in range(0, len(cells), cols + 1)]
        if max(rows_w) > max_width:
            break
        cols += 1
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    band = 14 * 3 + 6
    row_h = [max(c[3] for c in r) + band for r in rows]
    col_w = [max(r[i][2] for r in rows if i < len(r)) for i in range(cols)]
    W = sum(col_w) + pad * (cols + 1)
    H = sum(row_h) + pad * (len(rows) + 1)
    sheet = Image.new('RGBA', (W, H), (40, 40, 40, 255))
    d = ImageDraw.Draw(sheet)
    y = pad
    for r, rh in zip(rows, row_h):
        x = pad
        for i, (t, content, _cw, _ch, lines) in enumerate(r):
            area_h = rh - band
            sheet.paste(checker(col_w[i], area_h), (x, y))
            ox = x + 4
            for im2, _sc in content:
                oy = y + (area_h - im2.size[1]) // 2
                sheet.alpha_composite(im2, (ox, oy))
                ox += im2.size[0] + 8
            d.rectangle([x, y + area_h, x + col_w[i] - 1, y + rh - 1], fill=(72, 72, 72, 255))
            ty = y + area_h + 3
            for ln in lines:
                d.text((x + 4, ty), ln, font=fnt, fill=(255, 255, 255, 255))
                ty += 13
            d.text((x + 4, y + rh - 16), t.get('sub', ''), font=fnt, fill=(190, 220, 255, 255))
            x += col_w[i] + pad
        y += rh + pad
    sheet.convert('RGB').save(path, 'PNG')


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
STOP_LOWER = {'AIR', 'ALL', 'ANY', 'ART', 'BIG', 'CAN', 'CAR', 'COM', 'DEF', 'DEV', 'END', 'FAR', 'FOR', 'GEN', 'GOD', 'HOT', 'INF',
              'LAW', 'LOW', 'MAN', 'MAX', 'MIN', 'MIL', 'NEW', 'NON', 'NOT', 'ONE', 'OUR', 'OUT', 'PAN', 'PRO', 'RAD', 'RED', 'SEA',
              'SUB', 'SUN', 'TAX', 'THE', 'TOP', 'TWO', 'USE', 'WAR', 'WAY', 'WIN', 'ZIP', 'AND', 'TAN', 'ARM', 'ICE', 'GAS', 'OIL',
              'ARC', 'BAR', 'BOX', 'COL', 'DAM', 'EYE', 'FAN', 'FIN', 'GUN', 'HAT', 'JET', 'KEY', 'MAP', 'NET', 'PIN', 'RAT', 'SUP',
              'TOY', 'VAN', 'WEB', 'AID', 'BAN', 'BUS', 'CUT', 'DEM', 'FUN', 'HIT', 'LAB', 'MOB', 'OFF', 'OWN', 'PAY', 'RAW', 'SET'}


def nation_of(game, relpath):
    tags = game.tags()
    parts = relpath.replace(BS, '/').split('/')
    stem = os.path.splitext(parts[-1])[0]
    for comp in reversed(parts[:-1]):
        if comp.upper() in tags and comp == comp.upper():
            return comp
    toks = re.split(r'[_\-\s]', stem)
    for i, tok in enumerate(toks[:4]):
        if len(tok) == 3 and tok.upper() in tags:
            if tok.isupper() or (i <= 2 and tok.upper() not in STOP_LOWER):
                return tok.upper()
    return None


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def stem_of(path):
    return os.path.splitext(os.path.basename(path))[0]


# ----------------------------------------------------------------------------
# family processing
# ----------------------------------------------------------------------------
class Ctx:
    def __init__(self, game, out, seed):
        self.game, self.out, self.seed = game, out, seed
        self._ideas = None
        self._chars = None

    def ideas(self):
        if self._ideas is None:
            self._ideas = idea_textures(self.game)
        return self._ideas

    def chars(self):
        if self._chars is None:
            self._chars = character_textures(self.game)
        return self._chars


def classify_filter(ctx, fam, tex_key, relpath):
    """Return (True, label) when the texture belongs to the family classification, (False, reason) when not."""
    if fam.get('ideas') or fam.get('advisor_cards'):
        cats = ctx.ideas().get(tex_key, set())
        if fam.get('exclude_ideas') and cats & set(fam['exclude_ideas']):
            return False, 'belongs to another idea family (%s)' % ','.join(sorted(cats & set(fam['exclude_ideas'])))
        if fam.get('advisor_cards') and 'advisor_card' in ctx.chars().get(tex_key, set()):
            return True, 'advisor idea_token'
        if cats & set(fam.get('ideas') or []):
            return True, ','.join(sorted(cats & set(fam['ideas'])))
        return False, 'not used by an idea in the family categories'
    if fam.get('portrait'):
        kinds = ctx.chars().get(tex_key, set())
        pk = fam['portrait']
        low = os.path.basename(relpath).lower()
        name_commander = bool(re.search(r'(^|_)(land|navy|army|air)(_|\d|\.)', low))
        name_operative = 'operative' in low
        folder_sci = '/scientists/' in ('/' + relpath.lower())
        if pk == 'operative':
            ok = 'operative' in kinds or name_operative
        elif pk == 'scientist':
            ok = 'scientist' in kinds or folder_sci
        elif pk == 'commander':
            ok = (('commander' in kinds or 'commander_other' in kinds) and 'operative' not in kinds) or (name_commander and not kinds)
            ok = ok and not folder_sci and not name_operative
        elif pk == 'leader':
            civ = bool(kinds & {'leader', 'civilian_other'})
            generic = bool(re.search(r'generic_\d', low)) and not kinds
            ok = (civ or generic) and 'operative' not in kinds and 'commander' not in kinds and not name_operative and not folder_sci
        else:
            ok = True
        if ok:
            return True, pk
        return False, 'not classified as %s portrait' % pk
    return True, ''


def process_family(ctx, fam, catalog, skipped_all, outroot):
    game = ctx.game
    fid = fam['id']
    variants = fam.get('variants') or [dict(subfolder='', dirs=fam['dirs'], canvas=fam.get('canvas'))]
    prim = variants[0]
    fam_dir = os.path.join(outroot, fam['folder'].replace('/', os.sep))
    os.makedirs(fam_dir, exist_ok=True)
    skip = collections.defaultdict(list)

    def add_skip(rel, reason):
        skip[reason].append(rel)
        skipped_all.append(dict(family=fid, file=rel, reason=reason))

    by_tex = game.sprites_by_tex()
    exclude = re.compile(fam['exclude'], re.I) if fam.get('exclude') else None
    # candidate textures per variant
    vtex = []
    for v in variants:
        vtex.append(game.textures(v['dirs']))
    prim_tex = vtex[0]
    vstem = []
    for vt in vtex:
        m = {}
        for e in vt.values():
            m.setdefault(stem_of(e[1]).lower(), e)
        vstem.append(m)
    all_sizes = collections.Counter()
    matched = {}
    for key, (rn, p, rel) in sorted(prim_tex.items()):
        if exclude and exclude.search(stem_of(p)):
            add_skip(rel, 'excluded by family name filter')
            continue
        ok, lab = classify_filter(ctx, fam, key, rel)
        if not ok:
            continue  # not part of the family; not counted as a skip
        if fam.get('registered') and key not in by_tex:
            add_skip(rel, 'texture not registered by any sprite in a .gfx file')
            continue
        hd = header(p)
        if not hd:
            add_skip(rel, 'unreadable header')
            continue
        all_sizes['%dx%d' % hd] += 1
        matched[key] = (rn, p, rel, hd, lab)
    dominant = all_sizes.most_common(1)[0][0] if all_sizes else None
    accepted = prim.get('canvas') or ([dominant] if dominant else [])
    acc_set = set(accepted)
    # per-variant canvases for multi variants
    cands = []
    pixhash = {}
    other_size = 0
    for key, (rn, p, rel, hd, lab) in sorted(matched.items()):
        sz = '%dx%d' % hd
        if sz not in acc_set:
            other_size += 1
            continue
        stem = stem_of(p)
        if PLACEHOLDER_RE.search(stem):
            add_skip(rel, 'placeholder name')
            continue
        if len(variants) > 1:
            okv = True
            for v, vs in zip(variants[1:], vstem[1:]):
                e2 = vs.get(stem.lower())
                h2 = header(e2[1]) if e2 else None
                if not h2 or '%dx%d' % h2 not in set(v.get('canvas') or []):
                    okv = False
                    break
            if not okv:
                add_skip(rel, 'no matching tag at every flag size/canvas')
                continue
        try:
            im, fmt = decode(p)
        except Unsupported as ex:
            add_skip(rel, 'unsupported format: %s' % ex)
            continue
        except Exception as ex:  # noqa: BLE001 - any undecodable texture is recorded as skipped with its reason
            add_skip(rel, 'decode failed: %s' % str(ex)[:80])
            continue
        arr = np.asarray(im)
        al = arr[..., 3]
        if al.max() < 8:
            add_skip(rel, 'all transparent')
            continue
        vis = al > 16
        if vis.mean() < 0.01:
            add_skip(rel, 'near-empty (visible pixels < 1%)')
            continue
        rgbv = arr[vis][:, :3]
        if (rgbv.max(0) - rgbv.min(0)).max() <= 2 and vis.mean() > 0.99 and len(variants) == 1:
            add_skip(rel, 'uniform image')
            continue
        hsh = sha256_bytes(arr.tobytes() + bytes(str(im.size), 'ascii'))
        if hsh in pixhash:
            add_skip(rel, 'duplicate pixels of an earlier candidate')
            skipped_all[-1]['duplicate_of'] = pixhash[hsh]
            continue
        pixhash[hsh] = rel
        sprites = by_tex.get(key, [])
        frames = sorted({s['frames'] for s in sprites}) or ['unregistered']
        cands.append(dict(key=key, rel=rel, path=p, rn=rn, group=game.group(rn), stem=stem, w=hd[0], h=hd[1], img=im,
                          fmt=fmt, label=lab, frames=frames, sprites=[s['name'] for s in sprites[:4]],
                          nation=nation_of(game, rel) if fam.get('nation', True) else None))
    k = int(fam.get('k', 15))
    cap = fam.get('nation_cap')
    if cap is None:
        cap = max(2, int(math.ceil(0.2 * k)))
    picks, info = [], dict(method='no candidates')
    if cands:
        X = np.array([descriptor(c['img']) for c in cands])
        ck = fam.get('canvas_k')
        if ck:
            info = dict(method='per-canvas k-medoids', groups={})
            for sz, kk in ck.items():
                idx = [i for i, c in enumerate(cands) if '%dx%d' % (c['w'], c['h']) == sz]
                if not idx:
                    continue
                sub = [cands[i] for i in idx]
                pp, inf = choose(sub, X[idx], int(kk), ctx.seed, cap if any(c['nation'] for c in sub) else 0)
                picks += [idx[j] for j in pp]
                info['groups'][sz] = dict(candidates=len(idx), **inf)
            picks.sort(key=lambda i: cands[i]['key'])
        else:
            picks, info = choose(cands, X, k, ctx.seed, cap if any(c['nation'] for c in cands) else 0)
    names = collections.Counter()
    for i in picks:
        c = cands[i]
        names[c['stem'].lower()] += 1
    outfiles = []
    for i in picks:
        c = cands[i]
        for v in variants:
            sub = v.get('subfolder', '')
            d = os.path.join(fam_dir, sub) if sub else fam_dir
            os.makedirs(d, exist_ok=True)
            if sub:
                rn, p, rel = vstem[variants.index(v)][c['stem'].lower()]
                im, fmt = decode(p)
                hd = im.size
            else:
                rn, p, rel, im, fmt = c['rn'], c['path'], c['rel'], c['img'], c['fmt']
            fn = c['stem'] + '.png'
            dest = os.path.join(d, fn)
            im.save(dest, 'PNG')
            outfiles.append(dict(file=(sub + '/' if sub else '') + fn, variant=sub or None, source_path=rel, source_root=rn,
                                 png_sha256=sha256_file(dest), source_sha256=sha256_file(p), width=im.size[0],
                                 height=im.size[1], source_format=fmt, frames=c['frames'], sprites=c['sprites'],
                                 canvas_label=(fam.get('canvas_labels') or {}).get('%dx%d' % (c['w'], c['h'])),
                                 classification=c['label'] or None, nation=c['nation'], group=c['group'],
                                 cluster=c.get('cluster'), is_medoid=c.get('medoid')))
    # contact sheets (one per variant folder; plus a combined one for multi-variant families)
    for v in variants:
        sub = v.get('subfolder', '')
        d = os.path.join(fam_dir, sub) if sub else fam_dir
        tiles = []
        for o in outfiles:
            if (o['variant'] or '') == sub:
                im = Image.open(os.path.join(d, os.path.basename(o['file']))).convert('RGBA')
                tiles.append(dict(img=im, label=os.path.basename(o['file']), sub='%dx%d %s' % (o['width'], o['height'], o['source_root'].split('/')[-1][:12])))
        if tiles:
            contact_sheet(os.path.join(d, 'contact_sheet.png'), tiles)
    if len(variants) > 1 and picks:
        tiles = []
        for i in picks:
            c = cands[i]
            parts = [Image.open(os.path.join(fam_dir, v['subfolder'], c['stem'] + '.png')).convert('RGBA') for v in variants]
            wd = sum(p.size[0] + 4 for p in parts) + 2 * parts[-1].size[0]
            comp = Image.new('RGBA', (wd, parts[0].size[1]), (0, 0, 0, 0))
            x = 0
            for p in parts:
                comp.alpha_composite(p, (x, 0))
                x += p.size[0] + 4
            comp.alpha_composite(parts[-1].resize((parts[-1].size[0] * 2, parts[-1].size[1] * 2), Image.NEAREST), (x, 0))
            tiles.append(dict(img=comp, label=c['stem'], sub='large | medium | small | small 2x'))
        contact_sheet(os.path.join(fam_dir, 'contact_sheet.png'), tiles, small_max=0)
    skipped = {r: dict(count=len(v), examples=v[:20]) for r, v in sorted(skip.items())}
    nat = collections.Counter(c['nation'] or 'none' for c in cands)
    catalog.append(dict(
        id=fid, shelf_folder=fam['folder'], kind=fam.get('kind'), dominant_canvas=dominant,
        accepted_canvases=accepted, canvas_distribution_matched=dict(all_sizes.most_common(8)),
        frames=dict(collections.Counter(f for o in outfiles if not o['variant'] or o['variant'] == variants[0].get('subfolder', '') for f in o['frames'])),
        frame_note=fam.get('frame_note'), source_dirs=[v['dirs'] for v in variants] if len(variants) > 1 else fam['dirs'],
        classification=fam.get('classification_note'), candidate_count=len(cands), matched_other_canvas=other_size,
        candidates_by_source=dict(collections.Counter(c['group'] for c in cands)), candidates_by_nation=dict(nat.most_common(12)),
        selected_count=len(picks), selection=info, selected=outfiles, skipped=skipped, notes=fam.get('notes')))
    return len(picks), len(cands)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--families-json', required=True)
    ap.add_argument('--only', default='')
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    game = Game(a.game)
    spec = json.load(open(a.families_json, encoding='utf-8'))
    only = {x for x in a.only.split(',') if x}
    ctx = Ctx(game, a.out, a.seed)
    outroot = os.path.join(a.out, 'vanilla_reference')
    os.makedirs(outroot, exist_ok=True)
    catalog, skipped_all = [], []
    for fam in spec['families']:
        if only and fam['id'] not in only:
            continue
        n, c = process_family(ctx, fam, catalog, skipped_all, outroot)
        print('%-26s selected %2d of %4d candidates -> %s' % (fam['id'], n, c, fam['folder']), flush=True)
    ver, raw, exe_mtime = game.version()
    meta = dict(game_version=ver, game_raw_version=raw, hoi4_exe_mtime=exe_mtime, game_root=game.path,
                generated=datetime.datetime.now().isoformat(timespec='seconds'), seed=a.seed,
                method=__doc__.split('Method', 1)[1].strip(), roots=[r for r, _ in game.roots],
                tool_versions=dict(python=sys.version.split()[0], pillow=Image.__version__, numpy=np.__version__))
    cat_path = os.path.join(a.out, 'catalog.json')
    if only and os.path.exists(cat_path):
        old = json.load(open(cat_path, encoding='utf-8'))
        keep = [f for f in old['families'] if f['id'] not in only]
        catalog = keep + catalog
        order = {f['id']: i for i, f in enumerate(spec['families'])}
        catalog.sort(key=lambda f: order.get(f['id'], 999))
        prev = {s['family'] + '|' + s['file']: s for s in json.load(open(os.path.join(a.out, 'skipped_all.json'), encoding='utf-8'))}
        skipped_all = [s for s in prev.values() if s['family'] not in only] + skipped_all
    meta['families'] = catalog
    with open(cat_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)
        f.write('\n')
    with open(os.path.join(a.out, 'skipped_all.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(skipped_all, f, indent=0, ensure_ascii=False)
        f.write('\n')


if __name__ == '__main__':
    main()
