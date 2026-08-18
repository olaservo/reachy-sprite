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
ANTENNA = EYE_DARK  # black wire antennae, same as the camera lenses
SHADOW = (40, 40, 48, 70)
MOTION = (150, 150, 160, 200)
SWEAT = (110, 170, 235, 255)
SPARK = (255, 205, 90, 255)


def new_frame():
    img = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def draw_antenna(d, x0, y0, tip_dx, tip_dy):
    """One wobbly antenna: a thin wire from (x0, y0) to a small tip dot,
    like the real robot's.

    Positive tip_dy points the tip up; negative droops it below the base."""
    mid = (x0 + tip_dx // 2, y0 - tip_dy // 2)
    tip = (x0 + tip_dx, y0 - tip_dy)
    d.line([(x0, y0), mid], fill=ANTENNA, width=1)
    d.line([mid, tip], fill=ANTENNA, width=1)
    d.ellipse([tip[0] - 1, tip[1] - 1, tip[0] + 1, tip[1] + 1], fill=ANTENNA)


def draw_eyes(d, cx, cy, style="open", look=0, scan=0):
    """Reachy Mini's face: two round camera eyes — one slightly larger —
    joined by a thin seam, with a tiny center camera lens sitting on it.

    The face always stays axis-aligned: at this resolution a diagonal
    face line shreds the round lenses, so head roll is deliberately not
    modeled — expression relies on bob, lean, antennae, and eyes."""
    lx = cx - 7 + look
    rx = cx + 7 + look
    mx = cx + look
    # (eye x, radius, eye center y): the left lens is slightly bigger
    eyes = ((lx, 4, cy), (rx, 3, cy))

    # thin seam connecting the eyes + tiny center camera lens
    # (drawn first, eyes go on top)
    d.line([lx, cy, rx, cy], fill=(150, 148, 140, 255), width=1)
    d.ellipse([mx - 1, cy - 1, mx + 1, cy + 1], fill=EYE_DARK)
    d.point((mx, cy - 1), fill=(170, 170, 180, 255))

    if style == "open":
        for ex, r, ey in eyes:
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=EYE_DARK)
            if r >= 4:
                d.ellipse([ex - r + 2, ey - r + 1, ex - r + 4, ey - r + 3], fill=EYE_GLINT)
            else:
                d.point((ex - 1, ey - 1), fill=EYE_GLINT)
    elif style == "blink":
        for ex, r, ey in eyes:
            d.line([ex - r, ey, ex + r, ey], fill=EYE_DARK, width=2)
    elif style == "happy":
        for ex, r, ey in eyes:
            d.arc([ex - r, ey - 3, ex + r, ey + 5], 180, 360, fill=EYE_DARK, width=2)
    elif style == "dizzy":
        for ex, r, ey in eyes:
            s = r - 1
            d.line([ex - s, ey - s, ex + s, ey + s], fill=EYE_DARK, width=1)
            d.line([ex - s, ey + s, ex + s, ey - s], fill=EYE_DARK, width=1)
    elif style == "scan":
        for ex, r, ey in eyes:
            d.rectangle([ex - r, ey - 3, ex + r, ey + 3], fill=EYE_DARK)
            # sweep the scan line across each lens, scaled to its width
            sx = ex - (r - 1) + (scan * (2 * (r - 1))) // 6
            d.line([sx, ey - 2, sx, ey + 2], fill=(90, 220, 160, 255), width=1)


def draw_robot(
    img,
    dy=0,
    squash=0,
    look=0,
    scan=0,
    eye_style="open",
    ant_l=(-2, 8),
    ant_r=(2, 8),
    head_dx=0,
    head_dy=0,
    ant_behind=False,
    glasses=False,
    ground_shadow=True,
):
    """Draw the whole robot into one logical frame.

    The real Reachy Mini expresses itself with a 6-DOF neck, full body
    rotation, and two animated antennae, so the head gets its own
    movement channels independent of the body — but only the ones that
    stay crisp at this resolution (integer translations):

    dy: whole-figure vertical offset (negative = up).  squash: bounce squash.
    head_dx / head_dy: neck pan lean and vertical head bob (neck z).
    When the head lifts off the body (head_dy < 0 past the overlap), the
    neck mechanism shows in the gap, like the real robot's.
    ant_behind: draw the antennae behind the head — drooping antennae
    fall behind it on the real robot, so only the tips peek out.
    """
    d = ImageDraw.Draw(img)
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
    head_top = body_top - head_h + 2 + head_dy
    head_bottom = body_top + 2 + head_dy
    if head_bottom < body_top:
        # neck mechanism peeks out when the head lifts off the body
        d.rectangle([hx - 3, head_bottom, hx + 3, body_top + 1], fill=ANTENNA)
        d.line([hx - 1, head_bottom, hx - 1, body_top], fill=(90, 90, 100, 255), width=1)
    if ant_behind:
        draw_antenna(d, hx - 6, head_top, *ant_l)
        draw_antenna(d, hx + 6, head_top, *ant_r)
    d.rounded_rectangle(
        [hx - head_w // 2, head_top, hx + head_w // 2, head_bottom],
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
        lx, rx = hx - 7 + look, hx + 7 + look
        d.rectangle([lx - 5, face_cy - 5, lx + 5, face_cy + 5], outline=SPARK, width=1)
        d.rectangle([rx - 4, face_cy - 4, rx + 4, face_cy + 4], outline=SPARK, width=1)
        d.line([lx + 5, face_cy - 2, rx - 4, face_cy - 2], fill=SPARK, width=1)

    # Antennae, planted on the head top.
    if not ant_behind:
        draw_antenna(d, hx - 6, head_top, *ant_l)
        draw_antenna(d, hx + 6, head_top, *ant_r)


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
    """Breathing bob with a lazy head sway — the neck is always alive."""
    frames = []
    bob = [0, -1, -1, 0]
    head_bob = [0, -1, -1, 0]
    sway = [(-2, 8), (-5, 7), (-2, 8), (1, 8)]
    sway_r = [(2, 8), (-1, 8), (2, 8), (5, 7)]
    for i in range(4):
        img, d = new_frame()
        draw_robot(img, dy=bob[i], head_dy=head_bob[i],
                   eye_style="blink" if i == 3 else "open",
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
        draw_robot(img, dy=bob[i], squash=sq[i], look=look,
                   head_dx=2 * direction, ant_l=ant_l, ant_r=ant_r)
        if direction:
            motion_lines(d, -direction)
        else:
            motion_lines(d, -1)
            motion_lines(d, 1)
        frames.append(img)
    return frames


def row_wave():
    """Non-looping greeting: the real robot greets with a head nod and an
    antenna wiggle, so nod the head while one antenna waves big."""
    frames = []
    wave = [(2, 8), (6, 6), (2, 9), (6, 6)]
    nod = [0, 2, 0, 2]
    for i in range(4):
        img, d = new_frame()
        draw_robot(img, dy=-1 if i % 2 else 0, head_dy=nod[i],
                   eye_style="happy",
                   ant_l=(-2, 8), ant_r=wave[i])
        if i in (1, 3):
            x, y = LW - 8, 8
            d.line([x - 2, y, x + 2, y], fill=SPARK, width=1)
            d.line([x, y - 2, x, y + 2], fill=SPARK, width=1)
        frames.append(img)
    return frames


def row_jump():
    """Celebration: the real robot can't jump — it stays planted and pops
    its head up on the neck, antennae shooting straight up, sparkles."""
    frames = []
    img, d = new_frame()
    draw_robot(img, squash=1, head_dy=1, ant_l=(-3, 6), ant_r=(3, 6))
    frames.append(img)
    img, d = new_frame()
    draw_robot(img, head_dy=-3, eye_style="open", ant_l=(-1, 9), ant_r=(1, 9))
    frames.append(img)
    img, d = new_frame()
    draw_robot(img, head_dy=-5, eye_style="happy", ant_l=(0, 10), ant_r=(0, 10))
    d = ImageDraw.Draw(img)
    for sx, sy in ((6, 14), (LW - 6, 12)):
        d.line([sx - 2, sy, sx + 2, sy], fill=SPARK, width=1)
        d.line([sx, sy - 2, sx, sy + 2], fill=SPARK, width=1)
    frames.append(img)
    img, d = new_frame()
    draw_robot(img, head_dy=-2, ant_l=(-2, 9), ant_r=(2, 9))
    frames.append(img)
    return frames


def row_failed():
    """Sad: the real move drops the head low on the neck with antennae
    hanging flat; the whole figure slumps and barely breathes."""
    frames = []
    for i in range(4):
        img, d = new_frame()
        droop_l = (-14, -7) if i % 2 == 0 else (-14, -6)
        droop_r = (14, -6) if i % 2 == 0 else (14, -7)
        draw_robot(img, dy=1, head_dy=3 if i % 2 else 2, ant_behind=True,
                   ant_l=droop_l, ant_r=droop_r, squash=1)
        # sweat drop sliding down beside the head
        sx, sy = LW - 9, 14 + i
        d.polygon([(sx, sy - 3), (sx - 2, sy + 1), (sx + 2, sy + 1)], fill=SWEAT)
        d.ellipse([sx - 2, sy - 1, sx + 2, sy + 3], fill=SWEAT)
        frames.append(img)
    return frames


def row_waiting():
    """Curious: glancing around with the head panning side to side and
    one antenna perked toward whatever caught its eye."""
    frames = []
    looks = [-3, 0, 3, 0]
    leans = [-2, 0, 2, 0]
    styles = ["open", "open", "open", "blink"]
    for i in range(4):
        img, d = new_frame()
        ant_l = (-4, 9) if i == 0 else (-2, 8)
        ant_r = (4, 9) if i == 2 else (2, 8)
        draw_robot(img, dy=0 if i % 2 else -1, look=looks[i],
                   head_dx=leans[i], eye_style=styles[i],
                   ant_l=ant_l, ant_r=ant_r)
        if i == 1:
            x, y = LW - 10, 9
            for r in (1, 3):
                d.ellipse([x - r, y - r, x + r, y + r], outline=MOTION, width=1)
        frames.append(img)
    return frames


def row_review():
    """Thinking: head bobbing slightly while the lenses scan."""
    frames = []
    scans = [0, 2, 4, 6]
    for i in range(4):
        img, d = new_frame()
        draw_robot(img, dy=0, head_dy=-1 if i % 2 else 0,
                   eye_style="scan", scan=scans[i], glasses=True,
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
            if has_pixels and cell.crop((0, 0, CELL_W, 1)).getextrema()[3][1] > 0:
                print(f"FAIL: row {row + 1} col {col + 1} has art clipped at the cell top")
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
