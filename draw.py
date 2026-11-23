#!/usr/bin/env python3
"""Draw the front page for news-image-20261123 (MONDAY 23 NOVEMBER 2026).

One 1024x1024 PNG newspaper front page: masthead, date line, lead story
(COP31 collapse) with a globe motif, six story cards, and an ALSO TODAY
footer with three more stories. All text is measured and auto-fit so
nothing overflows its box.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (248, 243, 232)
INK = (26, 26, 26)
RED = (163, 22, 33)
GREY = (110, 105, 95)
RULE = (26, 26, 26)
CARD_RULE = (180, 172, 158)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font_path, size, max_w, max_lines, min_size=11):
    """Shrink the font until the text wraps into at most max_lines."""
    while size >= min_size:
        f = ImageFont.truetype(font_path, size)
        lines = wrap_text(draw, text, f, max_w)
        if len(lines) <= max_lines and all(
            draw.textlength(line, font=f) <= max_w for line in lines
        ):
            return f, lines
        size -= 1
    f = ImageFont.truetype(font_path, min_size)
    return f, wrap_text(draw, text, f, max_w)


def draw_centered(draw, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)
    return y + font.size


def draw_globe(draw, cx, cy, r):
    """Wireframe globe with an orbit ring and red markers."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    # meridians
    for k in (0.45, 0.9):
        rx = r * k
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=INK, width=1)
    # parallels
    for k in (-0.5, 0.0, 0.5):
        y = cy + r * k
        half = math.sqrt(max(0.0, r * r - (r * k) ** 2))
        draw.line([cx - half, y, cx + half, y], fill=INK, width=1)
    # tilted orbit ring
    pts = []
    for deg in range(0, 361, 3):
        a = math.radians(deg)
        x = 1.45 * r * math.cos(a)
        y = 0.55 * r * math.sin(a)
        xr = x * math.cos(math.radians(-24)) - y * math.sin(math.radians(-24))
        yr = x * math.sin(math.radians(-24)) + y * math.cos(math.radians(-24))
        pts.append((cx + xr, cy + yr))
    draw.line(pts, fill=INK, width=1)
    # red markers: Antalya, Benghazi, Kyiv
    for dx, dy in ((0.30, -0.25), (-0.35, 0.10), (0.15, -0.55)):
        mx, my = cx + r * dx, cy + r * dy
        draw.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED)
        draw.ellipse([mx - 9, my - 9, mx + 9, my + 9], outline=RED, width=1)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    ML, MR = 40, 984
    CW = MR - ML  # 944

    # ---- Masthead ----
    f, _ = fit_lines(d, "THE WORLD IN ONE PICTURE", SERIF_B, 72, CW, 1, min_size=40)
    draw_centered(d, 26, "THE WORLD IN ONE PICTURE", f, INK)
    d.rectangle([ML, 104, MR, 107], fill=RULE)
    d.rectangle([ML, 111, MR, 112], fill=RULE)

    # ---- Date line ----
    f_date = ImageFont.truetype(SANS_B, 21)
    draw_centered(
        d, 124, "ONE DAY'S NEWS  \u00b7  MONDAY 23 NOVEMBER 2026", f_date, INK
    )
    d.rectangle([ML, 158, MR, 159], fill=RULE)

    # ---- Lead story ----
    y = 172
    f_kick = ImageFont.truetype(SANS_B, 16)
    d.text((ML, y), "ANTALYA  \u2014  COP31 CLIMATE SUMMIT", font=f_kick, fill=RED)
    y += 30
    f_head, head_lines = fit_lines(
        d,
        "COP31 ENDS IN FAILURE AS CLIMATE DEAL COLLAPSES",
        SERIF_B,
        44,
        CW,
        2,
        min_size=30,
    )
    for line in head_lines:
        d.text((ML, y), line, font=f_head, fill=INK)
        y += f_head.size + 6
    y += 4
    # summary (left) + globe (right)
    sum_w = 600
    f_sum, sum_lines = fit_lines(
        d,
        "The Antalya summit closed on Sunday with no cover deal after nearly "
        "200 nations split over fossil fuels \u2014 the first COP to end "
        "without an agreement since 2009, and the longest climate summit "
        "on record.",
        SERIF,
        21,
        sum_w,
        3,
        min_size=16,
    )
    sy = y
    for line in sum_lines:
        d.text((ML, sy), line, font=f_sum, fill=INK)
        sy += f_sum.size + 7
    draw_globe(d, 812, y + 42, 46)
    f_cap = ImageFont.truetype(SANS_B, 13)
    cap = "NO CONSENSUS \u00b7 LONGEST COP ON RECORD"
    cw = d.textlength(cap, font=f_cap)
    d.text((812 - cw / 2, y + 90), cap, font=f_cap, fill=RED)
    d.rectangle([ML, 414, MR, 415], fill=RULE)

    # ---- Six cards, 2 cols x 3 rows ----
    cards = [
        (
            "WASHINGTON",
            "DEMOCRATS CLINCH 258 SEATS, BIGGEST HOUSE MAJORITY SINCE 1992",
            "Chuck Hubbard's win in North Carolina gave Democrats their "
            "258th House seat on Sunday, the party's largest majority since "
            "1992, with four races still uncalled.",
        ),
        (
            "BENGHAZI",
            "SEA DRONES SINK RUSSIAN WARSHIP IN LIBYA PORT",
            "Suspected Ukrainian sea drones struck the Russian corvette "
            "Merkury at Benghazi, leaving it capsized and mostly sunk. A "
            "second Russian cargo ship was also hit off the coast.",
        ),
        (
            "SERANG, INDONESIA",
            "FACTORY FIRE KILLS 3, DOZENS MISSING",
            "A blaze swept the Fonusa Agung Mulia candy factory in Banten "
            "on Saturday. Three workers are dead and 36 remain unaccounted "
            "for as rescuers search the ruins.",
        ),
        (
            "KYIV REGION",
            "RUSSIAN STRIKES KILL 6 ACROSS KYIV REGION",
            "A drone hit a five-storey block in Dymer, a grocery in "
            "Vyshneve and a home in Bila Tserkva. Rescuers pulled a "
            "seven-year-old boy alive from the rubble.",
        ),
        (
            "GENEVA",
            "TRUMP CALLS 28-POINT PEACE PLAN 'NOT A FINAL OFFER'",
            "US, Ukrainian and European envoys met in Geneva on Sunday to "
            "debate the plan, which Kyiv and its allies say demands too "
            "much territory and too deep an army cut.",
        ),
        (
            "LAS VEGAS",
            "VERSTAPPEN WINS WILD VEGAS GP AFTER 35 LEAD CHANGES",
            "Max Verstappen held off Lando Norris by 0.639 seconds in a "
            "50-lap slipstreaming duel. Oscar Piastri was third after the "
            "Mercedes pair faded in the final laps.",
        ),
    ]
    card_w, card_h = 452, 138
    xs = [ML, ML + card_w + 40]
    ys = [420, 568, 716]
    for i, (kicker, head, body) in enumerate(cards):
        x = xs[i % 2]
        y = ys[i // 2]
        d.rectangle([x, y, x + card_w, y + card_h], outline=CARD_RULE, width=1)
        ix, iy = x + 10, y + 9
        iw = card_w - 20
        f_k = ImageFont.truetype(SANS_B, 14)
        d.text((ix, iy), kicker, font=f_k, fill=RED)
        hy = iy + 20
        f_h, h_lines = fit_lines(d, head, SERIF_B, 22, iw, 2, min_size=16)
        for line in h_lines:
            d.text((ix, hy), line, font=f_h, fill=RED)
            hy += f_h.size + 4
        by = iy + 76
        f_b, b_lines = fit_lines(d, body, SERIF, 16, iw, 3, min_size=13)
        for line in b_lines:
            d.text((ix, by), line, font=f_b, fill=INK)
            by += f_b.size + 3

    # ---- Footer: ALSO TODAY ----
    d.rectangle([ML, 866, MR, 867], fill=RULE)
    f_at = ImageFont.truetype(SANS_B, 19)
    d.text((ML, 876), "ALSO TODAY", font=f_at, fill=INK)
    foot = [
        (
            "PANT'S 128 POWERS INDIA TO RECORD 720",
            "Rishabh Pant became the first Asian wicketkeeper with Test "
            "hundreds in all four SENA countries.",
        ),
        (
            "THREE KILLED IN SHOOTING AT OHIO BABY SHOWER",
            "Gunfire erupted at a baby shower in Parma on Saturday evening. "
            "Three were killed and one wounded; a man is in custody.",
        ),
        (
            "ISRAEL OPENS PROBE AFTER SETTLER ARSON IN WEST BANK",
            "Vehicles were torched and racist graffiti sprayed in four West "
            "Bank villages early on Sunday. Israel has opened a probe.",
        ),
    ]
    fx = [ML, 360, 680]
    fw = 304
    for i, (head, body) in enumerate(foot):
        x = fx[i]
        y = 904
        f_h, h_lines = fit_lines(d, head, SERIF_B, 15, fw, 2, min_size=13)
        for line in h_lines:
            d.text((x, y), line, font=f_h, fill=INK)
            y += f_h.size + 3
        y += 2
        f_b, b_lines = fit_lines(d, body, SERIF, 13, fw, 3, min_size=12)
        for line in b_lines:
            d.text((x, y), line, font=f_b, fill=INK)
            y += f_b.size + 4

    # ---- Source line ----
    f_src = ImageFont.truetype(SANS, 11)
    src = "REPORTED BY REUTERS, AP, AL JAZEERA, CNA, FORMULA 1 AND OTHERS"
    sw = d.textlength(src, font=f_src)
    d.text(((W - sw) / 2, 1004), src, font=f_src, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
