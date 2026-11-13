"""Couch & Coach – generator grafik (mozaika A–F, slajd 1 + slajd 2).
Uzycie: python3 render.py dane.json katalog_wyjsciowy
Format posta: 1080x1350 (4:5, wymog Instagram API). Siatka profilu pokazuje srodek 3:4
(ok. 1012 px szerokosci), wiec projekt liczony jest w tym widocznym obszarze, a po 34 px
z kazdej strony to spad (tlo i ciaglosc karty).
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
W, H = 1080, 1350
VW = H * 0.75            # widoczna szerokosc kafelka w siatce
BLEED = (W - VW) / 2     # ~34 px spadu z kazdej strony
S = VW / 400.0           # jednostki projektu: widoczny kafelek 400 x 533

COL = {
    "terakota": (184, 117, 72), "czarny": (10, 10, 10), "szary": (109, 109, 109),
    "bezowy": (196, 161, 134), "white": (255, 255, 255), "cream": (248, 245, 238),
    "ink": (17, 17, 17), "soft": (90, 90, 90),
}
POS = {  # pozycja: (typ, tlo, rzad, kolumna w bloku 2x2)
    "A": ("DID YOU KNOW?", "bezowy", 0, None),
    "B": ("IDIOM OF THE DAY", "terakota", 0, 0),
    "C": ("IDIOM OF THE DAY", "czarny", 0, 1),
    "D": ("QUOTE OF THE DAY", "szary", 1, None),
    "E": ("WORD OF THE DAY", "szary", 1, 0),
    "F": ("WORD OF THE DAY", "terakota", 1, 1),
}


def u(v):
    return int(round(v * S))


def ux(v):
    """wspolrzedna x w widocznym obszarze -> piksel na plotnie 1080"""
    return int(round(BLEED + v * S))


def font(name, size, wght=None):
    path = {
        "display": "ArchivoBlack-Regular.ttf",
        "section": "Poppins-SemiBold.ttf",
        "sans": "OpenSans.ttf",
        "italic": "OpenSans-Italic.ttf",
    }[name]
    f = ImageFont.truetype(os.path.join(FONTS, path), size)
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            vals = [wght if a["name"] in (b"Weight", "Weight") else 100 for a in axes]
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


def fit(name, size, text, maxw, wght=None, minsize=20):
    while size > minsize:
        f = font(name, size, wght)
        if f.getlength(text) <= maxw:
            return f
        size -= 2
    return font(name, minsize, wght)


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def shadowed_card(base, box, radius, fill):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10, x1, y1 + 10), radius, fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(sh)
    ImageDraw.Draw(base).rounded_rectangle(box, radius, fill=fill)


_logo_cache = {}


def logo_img(width):
    p = os.path.join(HERE, "assets", "logo.png")
    if not os.path.exists(p):
        p = os.path.join(HERE, "assets", "logo_placeholder.png")
    if p not in _logo_cache:
        _logo_cache[p] = Image.open(p).convert("RGBA")
    im = _logo_cache[p]
    h = int(im.size[1] * width / im.size[0])
    return im.resize((width, h), Image.LANCZOS)


def logo_badge(base, x, y, size, sharp):
    """Biala 'kropla' z logo; sharp = rog bez zaokraglenia: bl, tl, tr, br."""
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((0, 0, size - 1, size - 1), fill=255)
    h = size // 2
    sq = {"bl": (0, h, h, size), "tl": (0, 0, h, h), "tr": (h, 0, size, h), "br": (h, h, size, size)}[sharp]
    d.rounded_rectangle(sq, radius=size // 14, fill=255)
    white = Image.new("RGBA", (size, size), COL["white"] + (255,))
    base.paste(white, (x, y), m)
    lg = logo_img(int(size * 0.8))
    base.alpha_composite(lg, (x + (size - lg.size[0]) // 2, y + (size - lg.size[1]) // 2 + int(size * 0.02)))


# ---------- zawartosc karty slowa / idiomu ----------

def word_block(d, x, y, maxw, headline, label, text, scale=1.0):
    fh = fit("display", int(u(31) * scale), headline, maxw)
    d.text((x, y), headline, font=fh, fill=COL["ink"])
    hb = d.textbbox((x, y), headline, font=fh)
    ly = hb[3] + u(7)
    d.line((x, ly, x + max(hb[2] - x, int(maxw * 0.85)), ly), fill=COL["ink"], width=max(3, u(1.3)))
    y2 = ly + u(10)
    if label:
        fl = font("italic", int(u(17) * scale), 400)
        d.text((x, y2), label, font=fl, fill=COL["ink"])
        y2 += u(17) * scale + u(14)
    ft = fit("sans", int(u(18.5) * scale), text, maxw, 400)
    for line in wrap(text, ft, maxw):
        d.text((x, y2), line, font=ft, fill=COL["ink"])
        y2 += ft.size * 1.3
    return y2


def examples_block(d, x, y, maxw, examples, bottom):
    size = u(15)
    while size > u(10):
        fe, fp = font("sans", size, 600), font("italic", size, 400)
        yy, ops = y, []
        for ex in examples:
            for line in wrap(ex["en"], fe, maxw):
                ops.append((yy, line, fe, COL["ink"])); yy += size * 1.28
            for line in wrap(ex["pl"], fp, maxw):
                ops.append((yy, line, fp, COL["soft"])); yy += size * 1.28
            yy += size * 0.7
        if yy <= bottom:
            break
        size -= 2
    for yy, line, f, c in ops:
        d.text((x, yy), line, font=f, fill=c)


# ---------- blok 2x2 (B, C, E, F) – slajd 1 ----------

def _big_canvas(posts, bg_rgb):
    """Cala kompozycja 2x2 w widocznych wspolrzednych + BLEED dookola, jednolite tlo bg_rgb."""
    VWi, B = int(round(VW)), int(round(BLEED))
    big = Image.new("RGBA", (2 * VWi + 2 * B, 2 * H), bg_rgb + (255,))
    d = ImageDraw.Draw(big)
    quad = {"B": (0, 0), "C": (1, 0), "E": (0, 1), "F": (1, 1)}
    for p, (cx, cy) in quad.items():
        ox, oy = B + cx * VWi, cy * H
        size = u(205)
        lx = ox + (u(60) if cx == 0 else VWi - u(60) - size)
        ly = oy + (u(20) if cy == 0 else u(305))
        logo_badge(big, lx, ly, size, {"B": "bl", "C": "bl", "E": "tl", "F": "tr"}[p])
        fs = fit("section", u(27), POS[p][0], u(320))
        hx = ox + (u(60) if cx == 0 else u(40))
        hy = oy + (u(258) if cy == 0 else u(262))
        d.text((hx, hy), POS[p][0], font=fs, fill=COL["white"] if POS[p][1] == "czarny" else COL["ink"])
    card = (B + u(60), u(331), B + 2 * VWi - u(60), H + u(204))
    shadowed_card(big, card, u(22), COL["white"] + (255,))
    d = ImageDraw.Draw(big)
    for p, (cx, cy) in quad.items():
        if p not in posts:
            continue
        q = posts[p]
        x = B + (u(105) if cx == 0 else VWi + u(40))
        y = (u(352) if cy == 0 else H + u(22))
        word_block(d, x, y, u(275), q["headline"], q.get("label", ""), q.get("text", ""))
    return big


def render_block(posts, out):
    VWi = int(round(VW))
    quad = {"B": (0, 0), "C": (1, 0), "E": (0, 1), "F": (1, 1)}
    for p, (cx, cy) in quad.items():
        if p not in posts:
            continue
        big = _big_canvas(posts, COL[POS[p][1]])
        x0 = cx * VWi  # z BLEED po lewej: crop od (B + cx*VWi) - B
        tile = big.crop((x0, cy * H, x0 + W, (cy + 1) * H)).convert("RGB")
        tile.save(os.path.join(out, posts[p]["_name"] + "_slajd1.jpg"), quality=92)


def _single_canvas(bg):
    """Plotno widocznego obszaru (VW x H); wynik wklejamy na srodek 1080x1350."""
    return Image.new("RGBA", (int(round(VW)), H), COL[bg] + (255,))


def _save_single(im, bg, path):
    full = Image.new("RGB", (W, H), COL[bg])
    full.paste(im.convert("RGB"), (int(round(BLEED)), 0))
    full.save(path, quality=92)


# ---------- slajd 2 dla B, C, E, F ----------

def render_vocab_slide2(p, q, out):
    typ, bg, row, colx = POS[p]
    im = _single_canvas(bg)
    W_ = im.size[0]
    d = ImageDraw.Draw(im)
    size = u(150)
    if row == 0:
        logo_badge(im, u(60) if colx == 0 else W_ - u(60) - size, u(25), size, "bl" if colx == 0 else "br")
        hy, card = u(190), (u(45), u(232), W_ - u(45), u(505))
    else:
        logo_badge(im, u(60) if colx == 0 else W_ - u(60) - size, u(365), size, "tl" if colx == 0 else "tr")
        hy, card = u(310), (u(45), u(25), W_ - u(45), u(290))
    d.text((u(55), hy), typ, font=fit("section", u(27), typ, u(300)), fill=COL["white"] if bg == "czarny" else COL["ink"])
    shadowed_card(im, card, u(22), COL["white"] + (255,))
    d = ImageDraw.Draw(im)
    x, maxw = card[0] + u(28), card[2] - card[0] - u(56)
    y = word_block(d, x, card[1] + u(22), maxw, q["headline"], q.get("label", ""), q.get("text", ""), scale=0.8)
    fx = font("sans", u(11), 700)
    d.text((x, y + u(6)), "EXAMPLES", font=fx, fill=COL["soft"])
    examples_block(d, x, y + u(22), maxw, q.get("examples", []), card[3] - u(18))
    _save_single(im, bg, os.path.join(out, q["_name"] + "_slajd2.jpg"))


# ---------- A: DID YOU KNOW? ----------

def render_dyk(q, out, slide):
    im = _single_canvas("bezowy")
    W_ = im.size[0]
    card = (u(34), u(48), W_ - u(34), u(471))
    shadowed_card(im, card, u(22), COL["cream"] + (255,))
    d = ImageDraw.Draw(im)
    x, maxw = card[0] + u(34), card[2] - card[0] - u(68)
    ft = font("display", u(20))
    d.text((x, u(98)), "DID YOU KNOW?", font=ft, fill=COL["ink"])
    d.line((x, u(140), x + u(250), u(140)), fill=COL["ink"], width=max(3, u(1.3)))
    fh = fit("display", u(27), q["headline"], maxw)
    d.text((x, u(196)), q["headline"], font=fh, fill=COL["ink"])
    y = u(196) + fh.size * 1.45
    if slide == 1:
        fb = font("sans", u(13.5), 600)
        for line in wrap(q.get("text", ""), fb, maxw):
            d.text((x, y), line, font=fb, fill=COL["ink"]); y += fb.size * 1.35
    else:
        examples_block(d, x, y, maxw, q.get("examples", []), u(380))
    lg = logo_img(u(68))
    im.alpha_composite(lg, (card[2] - u(48) - lg.size[0], u(390)))
    _save_single(im, "bezowy" if "DID" in POS[q["pos"]][0] else "szary", os.path.join(out, q["_name"] + f"_slajd{slide}.jpg"))


# ---------- D: QUOTE OF THE DAY ----------

def render_quote(q, out, slide):
    im = _single_canvas("szary")
    W_ = im.size[0]
    card = (u(60), u(79), W_ - u(50), u(454))
    shadowed_card(im, card, u(22), COL["white"] + (255,))
    d = ImageDraw.Draw(im)
    cx = (card[0] + card[2]) // 2
    maxw = card[2] - card[0] - u(50)
    fh = font("display", u(30))
    for i, t in enumerate(["QUOTE OF", "THE DAY"]):
        d.text((cx, u(116) + i * u(40)), t, font=fh, fill=COL["ink"], anchor="mm")
    body = q["headline"] if slide == 1 else q.get("translation", "")
    fq = font("sans" if slide == 1 else "italic", u(21 if slide == 1 else 18), 400)
    lines = wrap(body, fq, maxw)
    y = u(252) - (len(lines) - 1) * fq.size * 0.65
    for line in lines:
        d.text((cx, y), line, font=fq, fill=COL["ink"], anchor="mm"); y += fq.size * 1.3
    d.line((u(46), u(316), W_ - u(24), u(316)), fill=COL["ink"], width=max(3, u(1.3)))
    fa = font("sans", u(15), 400)
    author = q.get("label", "") if slide == 1 else q.get("source", q.get("label", ""))
    for i, line in enumerate(wrap(author, fa, maxw)):
        d.text((cx, u(344) + i * fa.size * 1.3), line, font=fa, fill=COL["ink"], anchor="mm")
    lg = logo_img(u(80))
    im.alpha_composite(lg, (cx - lg.size[0] // 2, u(388)))
    d.text((W_ // 2, u(510)), "couch&coach", font=font("sans", u(13), 400), fill=COL["ink"], anchor="mm")
    _save_single(im, "bezowy" if "DID" in POS[q["pos"]][0] else "szary", os.path.join(out, q["_name"] + f"_slajd{slide}.jpg"))


def grid_preview(names, out, fname):
    """names: siatka 2x3 w kolejnosci A B C / D E F."""
    tw, th, g = 400, 533, 4
    pv = Image.new("RGB", (3 * tw + 2 * g, 2 * th + g), "white")
    for i, n in enumerate(names):
        p = os.path.join(out, n + "_slajd1.jpg")
        if n and os.path.exists(p):
            b = int(round(BLEED))
            im = Image.open(p).crop((b, 0, W - b, H))  # tak siatka IG przycina 4:5 do 3:4
            pv.paste(im.resize((tw, th), Image.LANCZOS), ((i % 3) * (tw + g), (i // 3) * (th + g)))
    pv.save(os.path.join(out, fname))


def main(data_path, out):
    os.makedirs(out, exist_ok=True)
    posts = json.load(open(data_path, encoding="utf-8"))
    by = {}
    for q in posts:
        q["_name"] = q.get("name") or f"{q['pos']}_{q['headline'][:20].replace(' ', '_')}"
        by[q["pos"]] = q
    block = {p: by[p] for p in "BCEF" if p in by}
    if block:
        render_block(block, out)
        for p, q in block.items():
            render_vocab_slide2(p, q, out)
    if "A" in by:
        render_dyk(by["A"], out, 1); render_dyk(by["A"], out, 2)
    if "D" in by:
        render_quote(by["D"], out, 1); render_quote(by["D"], out, 2)
    names = [by[p]["_name"] if p in by else "" for p in "ABCDEF"]
    grid_preview(names, out, "podglad_siatki.png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
