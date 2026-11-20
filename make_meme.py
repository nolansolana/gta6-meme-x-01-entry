#!/usr/bin/env python3
"""Compose the gta6-meme-x-01 meme.

Background: AI-generated Vice City sunset scene (no text/logos/people).
Foreground (composited here in PIL, not by an image model):
  - make.fun ghost mascot: the OFFICIAL mark from the make.fun press kit
    (assets/official-mark.png, rendered from mark.svg), pasted as the
    mascot badge standing on the road
  - meme caption top + bottom, meme-style white bold text with black stroke
  - dark gradient band behind the bottom caption for readability
Output: meme.png (2048x1152).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BG_PATH = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry/media-generation-vice-city-bg-0-fa7c6832-2d23-47e0-a524-b6ac846b3c18.png"
OUT_PATH = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry/meme.png"
MARK_PATH = "/home/hatch/workspace/makefun/gta6-meme-x-01-entry/assets/official-mark.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (20, 20, 43, 255)
MAGENTA = (255, 46, 126, 255)
WHITE = (255, 255, 255, 255)




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

    # --- official make.fun ghost mark on the road, centre, standing above the band ---
    mark = Image.open(MARK_PATH).convert("RGBA").resize((540, 540), Image.LANCZOS)
    ghost = Image.new("RGBA", (560, 540), (0, 0, 0, 0))
    ghost.paste(mark, (10, 0), mark)
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
