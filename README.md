# reachy-sprite

A custom [Codex pet](https://github.com/openai/codex) sprite of the
**Reachy Mini** robot (the little cream desk robot by Pollen Robotics /
Hugging Face — round head, two round camera eyes of slightly different
sizes joined by a thin seam with a tiny center camera lens, two wobbly
antennae, cylindrical body).

> **Note:** this is an unofficial, fan-made community sprite. It is not
> affiliated with, endorsed by, or produced by Pollen Robotics or
> Hugging Face. Reachy Mini is their robot and design.

The sprite is generated deterministically by a Pillow script — no image
model involved — so it can be tweaked and regenerated at any time.

## Contents

```
reachy-mini/            the installable pet package
├── pet.json            first-party manifest (+ spriteVersionNumber for pet-viewer)
└── spritesheet.webp    1536x1872 v1 atlas, 8 cols x 9 rows, 192x208 cells
generate_sprite.py      generates the atlas + previews and verifies the layout
preview/                per-row PNG strips and animated GIFs, plus the full atlas
```

## How the real robot expresses itself

The real Reachy Mini has no arms, no legs, and no display face — its
camera eyes never change. All of its expression comes from three
channels, which its emotion library records as trajectories of head
pose + antenna angles + body yaw:

- a **6-DOF neck** — pan, tilt, roll, plus vertical head bobbing
- **full body rotation** around the vertical axis
- **two independently animated antennae**

The sprite animates the same channels where they survive the pixel
grid: independent head movement via sideways lean (`head_dx`) and
vertical bob (`head_dy`) — when the head lifts, the neck mechanism
shows in the gap like the real robot's — plus per-frame antenna poses.
Head *roll* is deliberately not modeled: at this resolution a diagonal
face line shreds the round lenses, and keeping the eyes looking right
matters more. Eye expressions (blinks, happy arcs, X eyes, scan lines)
are a sprite-native cheat the real robot can't do, layered on top of
the true body language. And since the real robot is planted on the
desk, it never leaves the ground in any animation — even "jumping" is
a grounded neck-pop celebration.

## Atlas layout (v1)

9 state rows, 4 leading frames each, trailing cells fully transparent.
Each row is modeled on a move from the robot's emotion/gesture library:

| Row | State | Real-robot move | Animation |
| --- | --- | --- | --- |
| 1 | idle | idle breathing | body + head bob, antenna sway, blink |
| 2 | running-right | — | head leans into the motion, speed streaks |
| 3 | running-left | — | mirrored |
| 4 | waving | greeting (nod) | head nods while one antenna waves big, happy eyes |
| 5 | jumping | celebration | stays planted, head pops up on the neck, antennae straight up, sparkles |
| 6 | failed | sad | head slumps low on the neck, antennae droop behind the head, sweat drop |
| 7 | waiting | curious | head pans side to side with one antenna perked, glancing around |
| 8 | running | — | front-facing bounce, streaks both sides |
| 9 | review | thinking | head bobs slightly while glasses + scan lines sweep the lenses |

A verification pass in `generate_sprite.py` asserts the atlas is exactly
1536x1872, that every trailing cell is fully transparent (the renderer
detects frame count from leading non-empty cells), and that no art is
clipped against the top of its cell.

## Install

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/pets"
cp -r reachy-mini "${CODEX_HOME:-$HOME/.codex}/pets/"
```

Then pick **Reachy Mini** under Settings → Appearance → Pets in the Codex
desktop app (restart the app if it doesn't show up). The same folder also
works with third-party renderers that read the pet package format
([petdex](https://github.com/crafter-station/petdex),
[pet-viewer-for-codex](https://github.com/yutat23/pet-viewer-for-codex)).

## Regenerate

```sh
pip install pillow
python3 generate_sprite.py
```

Caveats worth knowing (see the Codex Pets research notes this was built
from):

- Frame counts/timing are owned by the renderer, not the pet package.
  This atlas uses 4 leading frames per row; verify against your installed
  app if animations look truncated or flickery.
- Custom *behavior* (event hooks, click interactions) is not exposed by
  first-party Codex — tracked upstream in openai/codex #20863 and #21657.
  For hook-driven behavior use petdex or pet-viewer-for-codex.
