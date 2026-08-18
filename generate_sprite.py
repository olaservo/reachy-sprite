#!/usr/bin/env python3
"""Generate a Codex pet spritesheet of the Reachy Mini robot.

Draws every frame in a low-resolution logical grid (48x52) and scales it up
4x with nearest-neighbor resampling to the 192x208 cell size, which gives the
chunky pixel-art look of the built-in pets.

Atlas contract (v1): 1536x1872 WebP, 8 columns x 9 rows, transparent
background, leading frames per row, trailing cells fully transparent.

Row order (v1):
  1 idle | 2 running-right | 3 running-left | 4 waving | 5 jumping
  6 failed | 7 waiting | 8 running | 9 review
"""

from PIL import Image, ImageDraw

# --- Atlas geometry -----------------------------------------------------------
COLS, ROWS = 8, 9
CELL_W, CELL_H = 192, 208
SCALE = 4
LW, LH = CELL_W // SCALE, CELL_H // SCALE  # 48 x 52 logical pixels

FRAMES_PER_ROW = 4  # leading frames used in every row; trailing cells stay clear

# --- Palette ------------------------------------------------------------------
OUTLINE = (42, 42, 50, 255)
CREAM = (240, 237, 230, 255)
CREAM_SHADOW = (213, 208, 196, 255)
CREAM_BRIGHT = (252, 250, 246, 255)
EYE_DARK = (28, 28, 34, 255)
EYE_GLINT = (255, 255, 255, 255)
ANTENNA = (52, 52, 60, 255)
SHADOW = (40, 40, 48, 70)
MOTION = (150, 150, 160, 200)
SWEAT = (110, 170, 235, 255)
SPARK = (255, 205, 90, 255)


def new_frame():
    img = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def draw_antenna(d, x0, y0, tip_dx, tip_dy):
    """One wobbly antenna from (x0, y0) to a dotted tip."""
    mid = (x0 + tip_dx // 2, y0 - abs(tip_dy) // 2)
    tip = (x0 + tip_dx, y0 - abs(tip_dy))
    d.line([(x0, y0), mid], fill=ANTENNA, width=1)
    d.line([mid, tip], fill=ANTENNA, width=1)
    d.ellipse([tip[0] - 1, tip[1] - 1, tip[0] + 1, tip[1] + 1], fill=ANTENNA)


def draw_eyes(d, cx, cy, style="open", look=0, scan=0, mirror=False):
    """Reachy Mini's asymmetric camera eyes: one big lens, one small."""
    big_x = cx - 5 + look
    small_x = cx + 7 + look
    if mirror:
        big_x = cx + 5 + look
        small_x = cx - 7 + look
    if style == "open":
        d.ellipse([big_x - 4, cy - 4, big_x + 4, cy + 4], fill=EYE_DARK)
        d.ellipse([big_x - 2, cy - 3, big_x, cy - 1], fill=EYE_GLINT)
        d.ellipse([small_x - 2, cy - 2, small_x + 2, cy + 2], fill=EYE_DARK)
        d.point((small_x - 1, cy - 1), fill=EYE_GLINT)
    elif style == "blink":
        d.line([big_x - 4, cy, big_x + 4, cy], fill=EYE_DARK, width=2)
        d.line([small_x - 2, cy, small_x + 2, cy], fill=EYE_DARK, width=2)
    elif style == "happy":
        d.arc([big_x - 4, cy - 3, big_x + 4, cy + 5], 180, 360, fill=EYE_DARK, width=2)
        d.arc([small_x - 2, cy - 2, small_x + 2, cy + 3], 180, 360, fill=EYE_DARK, width=2)
    elif style == "dizzy":
        for ex, r in ((big_x, 3), (small_x, 2)):
            d.line([ex - r, cy - r, ex + r, cy + r], fill=EYE_DARK, width=1)
            d.line([ex - r, cy + r, ex + r, cy - r], fill=EYE_DARK, width=1)
    elif style == "scan":
        d.rectangle([big_x - 4, cy - 3, big_x + 4, cy + 3], fill=EYE_DARK)
        d.line([big_x - 3 + scan, cy - 2, big_x - 3 + scan, cy + 2], fill=(90, 220, 160, 255), width=1)
        d.rectangle([small_x - 2, cy - 2, small_x + 2, cy + 2], fill=EYE_DARK)


def draw_robot(
    d,
    dy=0,
    squash=0,
    look=0,
    scan=0,
    eye_style="open",
    ant_l=(-2, 8),
    ant_r=(2, 8),
    head_dx=0,
    head_tilt=0,
    glasses=False,
    ground_shadow=True,
):
    """Draw the whole robot into one logical frame.

    dy: vertical offset (negative = up).  squash: extra px removed from body
    height (bounce squash).  head_dx: sideways head shift for leaning.
    head_tilt: vertical offset added to one side of the antennae bases.
    """
    cx = LW // 2
    ground = LH - 5

    if ground_shadow:
        sw = 13 - max(0, -dy) // 2
        d.ellipse([cx - sw, ground + 1, cx + sw, ground + 4], fill=SHADOW)

    # Body: a squat cylinder that tapers slightly toward the top.
    body_h = 13 - squash
    body_top = ground + dy - body_h
    d.polygon(
        [
            (cx - 9, body_top),
            (cx + 9, body_top),
            (cx + 11, ground + dy),
            (cx - 11, ground + dy),
        ],
        fill=CREAM,
        outline=OUTLINE,
    )
    d.line([cx - 10, ground + dy - 3, cx + 10, ground + dy - 3], fill=CREAM_SHADOW, width=1)
    d.line([cx - 9, ground + dy - 5, cx + 9, ground + dy - 5], fill=CREAM_SHADOW, width=1)

    # Head: wide rounded slab, most of the figure.
    head_h = 19 + squash // 2
    head_w = 30
    hx = cx + head_dx
    head_top = body_top - head_h + 2
    d.rounded_rectangle(
        [hx - head_w // 2, head_top, hx + head_w // 2, body_top + 2],
        radius=8,
        fill=CREAM,
        outline=OUTLINE,
        width=1,
    )
    # soft top highlight
    d.line([hx - 8, head_top + 2, hx + 8, head_top + 2], fill=CREAM_BRIGHT, width=1)

    face_cy = head_top + head_h // 2 + 1
    draw_eyes(d, hx, face_cy, style=eye_style, look=look, scan=scan)

    if glasses:
        big_x, small_x = hx - 5 + look, hx + 7 + look
        d.rectangle([big_x - 6, face_cy - 5, big_x + 6, face_cy + 5], outline=SPARK, width=1)
        d.rectangle([small_x - 4, face_cy - 4, small_x + 4, face_cy + 4], outline=SPARK, width=1)
        d.line([big_x + 6, face_cy - 1, small_x - 4, face_cy - 1], fill=SPARK, width=1)

    # Antennae, planted on the head top.
    base_l = (hx - 6, head_top + head_tilt)
    base_r = (hx + 6, head_top - head_tilt)
    draw_antenna(d, *base_l, *ant_l)
    draw_antenna(d, *base_r, *ant_r)


def motion_lines(d, side, y=30):
    """Speed streaks behind a running robot. side=-1 lines on left, 1 on right."""
    x = 4 if side == -1 else LW - 4
    step = 2 if side == -1 else -2
    for i, ln in enumerate((5, 4, 5)):
        y0 = y - 6 + i * 5
        if side == -1:
            d.line([x, y0, x + ln, y0], fill=MOTION, width=1)
        else:
            d.line([x - ln, y0, x, y0], fill=MOTION, width=1)


# --- Per-row frame builders ---------------------------------------------------

def row_idle():
    frames = []
    bob = [0, -1, -1, 0]
    sway = [(-2, 8), (-3, 7), (-2, 8), (-1, 8)]
    sway_r = [(2, 8), (1, 8), (2, 8), (3, 7)]
    for i in range(4):
        img, d = new_frame()
        draw_robot(d, dy=bob[i], eye_style="blink" if i == 3 else "open",
                   ant_l=sway[i], ant_r=sway_r[i])
        frames.append(img)
    return frames


def row_run(direction):
    """direction: 1 = right, -1 = left, 0 = generic front-facing run."""
    frames = []
    bob = [0, -3, 0, -3]
    sq = [1, 0, 1, 0]
    for i in range(4):
        img, d = new_frame()
        look = 3 * direction
        trail = -4 * direction if direction else 0
        ant_l = (trail - 2, 7 if i % 2 else 8)
        ant_r = (trail + 2, 8 if i % 2 else 7)
        draw_robot(d, dy=bob[i], squash=sq[i], look=look,
                   head_dx=2 * direction, ant_l=ant_l, ant_r=ant_r)
        if direction:
            motion_lines(d, -direction)
        else:
            motion_lines(d, -1)
            motion_lines(d, 1)
        frames.append(img)
    return frames


def row_wave():
    """Non-looping greeting: no arms, so Reachy waves with an antenna."""
    frames = []
    wave = [(2, 8), (6, 6), (2, 9), (6, 6)]
    for i in range(4):
        img, d = new_frame()
        draw_robot(d, dy=-1 if i % 2 else 0, eye_style="happy",
                   ant_l=(-2, 8), ant_r=wave[i], head_tilt=1 if i % 2 else 0)
        if i in (1, 3):
            x, y = LW - 8, 8
            d.line([x - 2, y, x + 2, y], fill=SPARK, width=1)
            d.line([x, y - 2, x, y + 2], fill=SPARK, width=1)
        frames.append(img)
    return frames


def row_jump():
    frames = []
    img, d = new_frame()
    draw_robot(d, dy=0, squash=3, ant_l=(-3, 6), ant_r=(3, 6))
    frames.append(img)
    img, d = new_frame()
    draw_robot(d, dy=-7, eye_style="open", ant_l=(-2, 10), ant_r=(2, 10))
    frames.append(img)
    img, d = new_frame()
    draw_robot(d, dy=-11, eye_style="happy", ant_l=(-4, 9), ant_r=(4, 9))
    frames.append(img)
    img, d = new_frame()
    draw_robot(d, dy=-3, squash=1, ant_l=(-3, 10), ant_r=(3, 10))
    frames.append(img)
    return frames


def row_failed():
    frames = []
    for i in range(4):
        img, d = new_frame()
        droop_l = (-8, 2) if i % 2 == 0 else (-8, 1)
        droop_r = (8, 1) if i % 2 == 0 else (8, 2)
        draw_robot(d, dy=1, eye_style="dizzy", ant_l=droop_l, ant_r=droop_r,
                   squash=1)
        # sweat drop sliding down beside the head
        sx, sy = LW - 9, 14 + i
        d.polygon([(sx, sy - 3), (sx - 2, sy + 1), (sx + 2, sy + 1)], fill=SWEAT)
        d.ellipse([sx - 2, sy - 1, sx + 2, sy + 3], fill=SWEAT)
        frames.append(img)
    return frames


def row_waiting():
    frames = []
    looks = [-3, 0, 3, 0]
    styles = ["open", "open", "open", "blink"]
    for i in range(4):
        img, d = new_frame()
        draw_robot(d, dy=0 if i % 2 else -1, look=looks[i], eye_style=styles[i],
                   ant_l=(-2, 8), ant_r=(2, 8), head_tilt=1 if i == 2 else 0)
        if i == 1:
            x, y = LW - 10, 9
            for r in (1, 3):
                d.ellipse([x - r, y - r, x + r, y + r], outline=MOTION, width=1)
        frames.append(img)
    return frames


def row_review():
    frames = []
    scans = [0, 2, 4, 6]
    for i in range(4):
        img, d = new_frame()
        draw_robot(d, dy=0, eye_style="scan", scan=scans[i], glasses=True,
                   ant_l=(-2, 8), ant_r=(2, 8))
        frames.append(img)
    return frames


ROW_BUILDERS = [
    ("idle", row_idle),
    ("running-right", lambda: row_run(1)),
    ("running-left", lambda: row_run(-1)),
    ("waving", row_wave),
    ("jumping", row_jump),
    ("failed", row_failed),
    ("waiting", row_waiting),
    ("running", lambda: row_run(0)),
    ("review", row_review),
]


def build_atlas():
    atlas = Image.new("RGBA", (COLS * CELL_W, ROWS * CELL_H), (0, 0, 0, 0))
    for row, (name, builder) in enumerate(ROW_BUILDERS):
        frames = builder()
        assert len(frames) == FRAMES_PER_ROW, f"{name}: {len(frames)} frames"
        for col, frame in enumerate(frames):
            big = frame.resize((CELL_W, CELL_H), Image.NEAREST)
            atlas.paste(big, (col * CELL_W, row * CELL_H))
    return atlas


def verify(atlas):
    """Trailing cells transparent; leading frames non-empty; no cell bleed."""
    ok = True
    for row in range(ROWS):
        for col in range(COLS):
            cell = atlas.crop((col * CELL_W, row * CELL_H,
                               (col + 1) * CELL_W, (row + 1) * CELL_H))
            has_pixels = cell.getextrema()[3][1] > 0
            if col < FRAMES_PER_ROW and not has_pixels:
                print(f"FAIL: row {row + 1} col {col + 1} is empty but should be a frame")
                ok = False
            if col >= FRAMES_PER_ROW and has_pixels:
                print(f"FAIL: row {row + 1} col {col + 1} should be fully transparent")
                ok = False
    if atlas.size != (1536, 1872):
        print(f"FAIL: atlas size {atlas.size}, expected (1536, 1872)")
        ok = False
    return ok


def previews(atlas, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    for row, (name, _) in enumerate(ROW_BUILDERS):
        strip = atlas.crop((0, row * CELL_H, FRAMES_PER_ROW * CELL_W, (row + 1) * CELL_H))
        bg = Image.new("RGBA", strip.size, (58, 58, 70, 255))
        bg.alpha_composite(strip)
        bg.save(f"{outdir}/{row + 1:02d}-{name}.png")
        gif = [atlas.crop((c * CELL_W, row * CELL_H, (c + 1) * CELL_W, (row + 1) * CELL_H))
               for c in range(FRAMES_PER_ROW)]
        gif_bg = []
        for f in gif:
            b = Image.new("RGBA", f.size, (58, 58, 70, 255))
            b.alpha_composite(f)
            gif_bg.append(b.convert("P", palette=Image.ADAPTIVE))
        gif_bg[0].save(f"{outdir}/{row + 1:02d}-{name}.gif", save_all=True,
                       append_images=gif_bg[1:], duration=180, loop=0, disposal=2)


if __name__ == "__main__":
    atlas = build_atlas()
    if not verify(atlas):
        raise SystemExit(1)
    atlas.save("reachy-mini/spritesheet.webp", lossless=True)
    atlas.save("preview/atlas.png")
    previews(atlas, "preview")
    print("OK: wrote reachy-mini/spritesheet.webp (1536x1872, 8x9 grid, "
          f"{FRAMES_PER_ROW} leading frames per row)")
