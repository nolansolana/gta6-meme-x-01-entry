#!/usr/bin/env python3
"""Compose the gta6-meme-x-01 meme.

Background: AI-generated Vice City sunset scene (no text/logos/people).
Foreground (drawn here in PIL, not by an image model):
  - make.fun ghost mascot: white ghost, sparkle eyes, magenta star coin
    (drawn from the logo description: white ghost, sparkle eyes, magenta star)
  - meme caption top + bottom, meme-style white bold text with black stroke
  - dark gradient band behind the bottom caption for readability
Output: meme.png (2048x1152).
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BG_PATH = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry/media-generation-vice-city-bg-0-fa7c6832-2d23-47e0-a524-b6ac846b3c18.png"
OUT_PATH = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry/meme.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (20, 20, 43, 255)
MAGENTA = (255, 46, 126, 255)
WHITE = (255, 255, 255, 255)

SS = 4  # supersample factor for the ghost layer


def star_points(cx, cy, r_outer, r_inner, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sparkle_points(cx, cy, r_outer, r_inner):
    # 4-point sparkle (like a twinkle star): 8 alternating points
    pts = []
    for i in range(8):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(-90 + i * 45)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_ghost():
    """Return an RGBA layer with the ghost mascot (white ghost, sparkle eyes,
    magenta star coin held up in its right arm). Final size 560x540."""
    W, H = 560 * SS, 540 * SS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx = 250 * SS
    top = 20 * SS
    r = 135 * SS            # half width of body (taller-than-wide ghost)
    cy = top + r            # dome centre y
    yb = 400 * SS           # hem baseline y
    amp = 48 * SS           # scallop depth

    # --- body outline polygon: dome + straight sides + scalloped hem ---
    pts = []
    for deg in range(180, 361, 3):
        a = math.radians(deg)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append((cx + r, yb))
    n = 64
    for i in range(n + 1):
        t = i / n
        x = cx + r - 2 * r * t
        y = yb + amp * abs(math.sin(4 * math.pi * t))
        pts.append((x, y))
    pts.append((cx - r, yb))
    pts.append((cx - r, cy))
    d.polygon(pts, fill=WHITE, outline=NAVY, width=7 * SS)

    # --- raised right arm (navy underlay, white over) ---
    ax0, ay0 = cx + r * 0.88, cy + 1.00 * r
    ax1, ay1 = cx + r * 1.25, cy + 0.35 * r
    ax2, ay2 = cx + r * 1.38, cy + 0.05 * r
    arm = [(ax0, ay0), (ax1, ay1), (ax2, ay2)]
    d.line(arm, fill=NAVY, width=36 * SS, joint="curve")
    d.line(arm, fill=WHITE, width=24 * SS, joint="curve")
    for (x, y) in [(ax0, ay0), (ax2, ay2)]:
        d.ellipse([x - 18 * SS, y - 18 * SS, x + 18 * SS, y + 18 * SS], fill=NAVY)
        d.ellipse([x - 12 * SS, y - 12 * SS, x + 12 * SS, y + 12 * SS], fill=WHITE)

    # --- magenta star coin at the raised hand, with glow ---
    sx, sy = cx + r * 1.45, cy - 0.08 * r
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.polygon(star_points(sx, sy, 84 * SS, 34 * SS), fill=(255, 46, 126, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(18 * SS))
    layer.alpha_composite(glow)
    d = ImageDraw.Draw(layer)
    d.polygon(star_points(sx, sy, 70 * SS, 29 * SS), fill=WHITE)
    d.polygon(star_points(sx, sy, 62 * SS, 26 * SS), fill=MAGENTA)
    d.polygon(sparkle_points(sx - 15 * SS, sy - 17 * SS, 17 * SS, 5 * SS), fill=WHITE)

    # --- sparkle eyes ---
    eye_y = cy + 0.45 * r
    for ex in (cx - 0.42 * r, cx + 0.42 * r):
        d.polygon(sparkle_points(ex, eye_y, 38 * SS, 12 * SS), fill=NAVY)
        d.polygon(sparkle_points(ex - 7 * SS, eye_y - 9 * SS, 10 * SS, 3 * SS), fill=WHITE)

    # --- small smile (kept well inside the body, above the hem) ---
    mx0, my0 = cx - 30 * SS, eye_y + 48 * SS
    mx1, my1 = cx + 30 * SS, eye_y + 88 * SS
    d.arc([mx0, my0, mx1, my1], start=15, end=165, fill=NAVY, width=8 * SS)

    return layer.resize((560, 540), Image.LANCZOS)


def fit_font(text, start_size, max_width):
    size = start_size
    while size > 20:
        f = ImageFont.truetype(FONT_BOLD, size)
        if f.getbbox(text)[2] <= max_width:
            return f
        size -= 4
    return ImageFont.truetype(FONT_BOLD, size)


def main():
    bg = Image.open(BG_PATH).convert("RGB")
    W, H = bg.size  # 2048x1152
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")

    # --- bottom dark gradient band for the lower caption ---
    band_h = 150
    band = Image.new("RGBA", (W, band_h), (0, 0, 0, 0))
    db = ImageDraw.Draw(band)
    for y in range(band_h):
        a = int(190 * (y / band_h) ** 1.4)
        db.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    img.paste(band, (0, H - band_h), band)
    d = ImageDraw.Draw(img, "RGBA")

    # --- ghost mascot on the road, centre, standing above the band ---
    ghost = draw_ghost()
    gw, gh = ghost.size
    gx = (W - gw) // 2 + 30  # +30 centres the ghost BODY (star overhangs right)
    gy = H - band_h - gh + 26  # feet just overlap the band top

    # soft shadow on the road
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    ds.ellipse([gx + 60, gy + gh - 14, gx + gw - 60, gy + gh + 26], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow, (0, 0), shadow)

    # faint reflection on the wet road
    refl = ghost.transpose(Image.FLIP_TOP_BOTTOM)
    refl_h = 90
    refl = refl.crop((0, 0, gw, refl_h))
    alpha = refl.split()[3].point(lambda v: int(v * 0.45))
    grad = Image.new("L", (gw, refl_h))
    gd = ImageDraw.Draw(grad)
    for y in range(refl_h):
        gd.line([(0, y), (gw, y)], fill=int(255 * (1 - y / refl_h)))
    alpha = Image.composite(alpha, Image.new("L", (gw, refl_h), 0), grad)
    refl.putalpha(alpha)
    img.paste(refl, (gx, gy + gh + 2), refl)

    img.paste(ghost, (gx, gy), ghost)
    d = ImageDraw.Draw(img, "RGBA")

    # --- captions (meme style: white bold, black stroke) ---
    top_text = "WAITED 13 YEARS FOR GTA VI"
    f_top = fit_font(top_text, 118, W - 120)
    bbox = d.textbbox((0, 0), top_text, font=f_top, stroke_width=10)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 52), top_text, font=f_top, fill=WHITE,
           stroke_width=10, stroke_fill=(0, 0, 0, 255))

    bot_text = "MY AGENT EARNED THE $80 ON MAKE.FUN"
    f_bot = fit_font(bot_text, 76, W - 140)
    bbox = d.textbbox((0, 0), bot_text, font=f_bot, stroke_width=6)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text(((W - tw) // 2, H - band_h + (band_h - th) // 2 - 6), bot_text,
           font=f_bot, fill=WHITE, stroke_width=6, stroke_fill=(0, 0, 0, 255))

    img.save(OUT_PATH, "PNG")
    print(f"saved {OUT_PATH} {img.size}")


if __name__ == "__main__":
    main()
