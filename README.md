# reachy-sprite

A custom [Codex pet](https://github.com/openai/codex) sprite of the
**Reachy Mini** robot (the little cream desk robot by Pollen Robotics /
Hugging Face — round head, two round camera eyes joined by a thin seam
with a tiny center camera lens, two wobbly antennae, cylindrical body).

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

## Atlas layout (v1)

9 state rows, 4 leading frames each, trailing cells fully transparent:

| Row | State | Animation |
| --- | --- | --- |
| 1 | idle | gentle bob, antenna sway, occasional blink |
| 2 | running-right | lean right, bounce, speed streaks |
| 3 | running-left | mirrored | 
| 4 | waving | no arms — waves an antenna, happy eyes, sparkle |
| 5 | jumping | squash, launch, hang with happy eyes, land |
| 6 | failed | flopped antennae, X eyes, sliding sweat drop |
| 7 | waiting | looks left/right, head tilt, blink, "?" ripple |
| 8 | running | front-facing bounce, streaks both sides |
| 9 | review | reading glasses, green scan lines sweeping both lenses |

A verification pass in `generate_sprite.py` asserts the atlas is exactly
1536x1872 and that every trailing cell is fully transparent (the renderer
detects frame count from leading non-empty cells).

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
