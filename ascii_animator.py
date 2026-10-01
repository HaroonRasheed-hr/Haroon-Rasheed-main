"""
ASCII Photo Animator v2 — Laser Scan Edition
----------------------------------------------
Converts a photo into a GRAY ASCII-art image, revealed once by a
downward laser-scan sweep (not a typewriter/typing effect), then
holds on the final frame. Does NOT loop.

USAGE:
    python ascii_animator.py your_photo.jpg

OUTPUT:
    ascii_output.gif

REQUIREMENTS:
    pip install pillow numpy --break-system-packages
"""

import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import numpy as np

# ---------- SETTINGS ----------
OUTPUT_WIDTH_CHARS = 110         # more chars = sharper detail
CHAR_ASPECT = 0.5                # corrects for font glyphs being taller than wide
CHARSET = " .:-=+*#%@"           # sparse -> dense (10 tonal levels)
CROP_TOP_FRACTION = 0.56         # keep head + shoulders only (fraction of photo height)
VIGNETTE = False
GAMMA = 0.55                     # <1 brightens mid-tones (face detail)                 # fade bright background around the subject
FONT_SIZE = 10
BG_COLOR = (10, 10, 10)          # near-black background
TEXT_COLOR = (200, 200, 200)     # revealed art: mid gray
LASER_COLOR = (235, 235, 235)    # the scanning line itself: bright gray/white
LASER_THICKNESS = 2              # px height of the laser bar

ROWS_PER_FRAME = 1               # reveal 1 row per frame = smooth sweep, no "typing" look
FRAME_DURATION_MS = 18           # fast smooth scan
HOLD_LAST_FRAME_MS = 2000        # pause on finished image
# --------------------------------


def image_to_ascii(img_path):
    img = Image.open(img_path).convert("L")
    w, h = img.size
    img = img.crop((0, 0, w, int(h * CROP_TOP_FRACTION)))
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=160, threshold=2))
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageOps.invert(img)  # bright backdrop -> sparse chars, dark hair/suit -> dense
    img = img.point(lambda v: int(255 * (v / 255) ** GAMMA))  # lift skin mid-tones so the face shows
    if VIGNETTE:
        # elliptical mask centred on the subject darkens the washed-out background
        w, h = img.size
        yy, xx = np.mgrid[0:h, 0:w]
        d = ((xx - w * 0.5) / (w * 0.55)) ** 2 + ((yy - h * 0.45) / (h * 0.62)) ** 2
        mask = np.clip(1.4 - d, 0, 1)
        img = Image.fromarray((np.array(img) * mask).astype(np.uint8))

    w, h = img.size
    new_w = OUTPUT_WIDTH_CHARS
    new_h = int(new_w * (h / w) * CHAR_ASPECT)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    pixels = np.array(img)

    scale = len(CHARSET) - 1
    ascii_rows = []
    for row in pixels:
        # brightness -> character (bright pixel = sparse char, dark pixel = dense char)
        line = "".join(CHARSET[int(val / 255 * scale)] for val in row)
        ascii_rows.append(line)
    return ascii_rows


def build_gif(img_path, out_path="ascii_output.gif"):
    ascii_rows = image_to_ascii(img_path)

    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", FONT_SIZE)
    except OSError:
        try:
            font = ImageFont.truetype("consola.ttf", FONT_SIZE)
        except OSError:
            font = ImageFont.load_default()

    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    line_w = max(d.textlength(r, font=font) for r in ascii_rows)
    line_h = font.size + 2

    canvas_w = int(line_w) + 20
    canvas_h = line_h * len(ascii_rows) + 20

    frames = []
    total_rows = len(ascii_rows)

    for boundary in range(0, total_rows + ROWS_PER_FRAME, ROWS_PER_FRAME):
        boundary = min(boundary, total_rows)
        img = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # already-scanned rows, in gray
        for i in range(boundary):
            draw.text((10, 10 + i * line_h), ascii_rows[i], font=font, fill=TEXT_COLOR)

        # the laser bar itself, at the current scan position
        if boundary < total_rows:
            laser_y = 10 + boundary * line_h
            draw.rectangle(
                [10, laser_y, canvas_w - 10, laser_y + LASER_THICKNESS],
                fill=LASER_COLOR,
            )

        frames.append(img)

    durations = [FRAME_DURATION_MS] * (len(frames) - 1) + [HOLD_LAST_FRAME_MS]

    # NOTE: no `loop` kwarg passed -> GIF plays once and stops (does not repeat)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
    )
    print(f"Done! Saved to: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ascii_animator.py your_photo.jpg")
        sys.exit(1)
    build_gif(sys.argv[1])