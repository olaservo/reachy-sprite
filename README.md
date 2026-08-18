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
reachy-mini/            the v1 pet package (first-party Codex + third-party renderers)
├── pet.json            manifest (+ spriteVersionNumber and animations for pet-viewer)
└── spritesheet.webp    1536x1872 v1 atlas, 8 cols x 9 rows, 192x208 cells
reachy-mini-v2/         the v2 pet package (third-party renderers)
├── pet.json            v2 manifest, remaps two states onto the extra rows
└── spritesheet.webp    1536x2288 v2 atlas, 8 cols x 11 rows
generate_sprite.py      generates both atlases + previews and verifies the layout
preview/                per-row PNG strips and animated GIFs, plus the full atlases
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

## Atlas layout

9 state rows (11 in v2), leading frames per row, trailing cells fully
transparent. Frame counts follow the tables hardcoded into the petdex
desktop renderer and pet-viewer-for-codex's defaults, which agree with
each other — neither detects frame count from the pixels, so shorter
rows would play blank trailing frames there. First-party Codex detects
leading non-empty cells and plays whatever exists. Each row is modeled
on a move from the robot's emotion/gesture library:

| Row | State | Frames | Real-robot move | Animation |
| --- | --- | --- | --- | --- |
| 1 | idle | 6 | idle breathing | body + head bob, antenna sway, mid-cycle blink |
| 2 | running-right | 8 | — | head leans into the motion, speed streaks |
| 3 | running-left | 8 | — | mirrored |
| 4 | waving | 4 | greeting (nod) | head nods while one antenna waves big, happy eyes |
| 5 | jumping | 5 | celebration | stays planted, head pops up on the neck, antennae straight up, sparkles |
| 6 | failed | 8 | sad | head slumps low on the neck, antennae droop behind the head, sweat drop slides down |
| 7 | waiting | 6 | curious | head pans side to side with one antenna perked, glancing around |
| 8 | running | 6 | — | front-facing bounce, streaks both sides |
| 9 | review | 6 | thinking | head bobs slightly while glasses + scan lines sweep the lenses |
| 10 | curious *(v2 only)* | 6 | attention crane | head cranes up on the neck toward something off-screen, antenna perked, pixel "?" |
| 11 | celebration *(v2 only)* | 4 | happy dance | rocks side to side, happy eyes, confetti sparkles — still planted |

A verification pass in `generate_sprite.py` asserts each atlas is
exactly its expected size (1536x1872 v1, 1536x2288 v2), that every
trailing cell is fully transparent, and that no art is clipped against
the top of its cell.

## Install

### First-party Codex desktop app (v1 package)

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/pets"
cp -r reachy-mini "${CODEX_HOME:-$HOME/.codex}/pets/"
```

Then pick **Reachy Mini** under Settings → Appearance → Pets (restart
the app if it doesn't show up). First-party Codex owns all behavior —
it derives the pet state from task status and reads only
`id`/`displayName`/`description`/`spritesheetPath` from `pet.json`,
ignoring the extra keys the manifests carry for third-party renderers.

### pet-viewer-for-codex (VS Code extension)

[yutat23/pet-viewer-for-codex](https://github.com/yutat23/pet-viewer-for-codex)
reads pets from `codexPet.petDirectory` if set, else
`$CODEX_HOME/pets`, else `~/.codex/pets` — so the install above covers
it. Install `reachy-mini-v2/` alongside (or instead) to get the two
extra rows: its animation names are a fixed set of six, and rows beyond
them never play unless a known name is remapped, so the v2 `pet.json`
maps **waiting → curious** (permission prompts make the robot crane
inquisitively) and the **click-to-wave interaction → celebration**
(clicking the pet plays the confetti dance).

Both manifests carry an explicit `animations` block
(`row`/`startColumn`/`frameCount`/`frameDurationMs`/`frameDurationsMs`
per state) so the extension plays exactly the frames that exist. Its
hooks mode ("Install Codex Hooks Integration") writes five hook entries
into `$CODEX_HOME/hooks.json` invoking a receiver script at
`$CODEX_HOME/codex-pet/bin/hook.cjs`, which drops one JSON file per
event into `$CODEX_HOME/codex-pet/events/` for the extension to watch.
States are derived from event names (SessionStart → idle,
PermissionRequest → waiting, Stop → review, everything else → running;
failed is reachable only via its App Server mode or the
`codexPet.setFailed` command) — scripts cannot introduce custom states,
but anything that writes a valid event file into that directory can
drive the five existing ones.

### petdex (desktop floater)

[crafter-station/petdex](https://github.com/crafter-station/petdex)
uses the same package format; `petdex install <slug>` copies published
pets into both `~/.petdex/pets/` and `~/.codex/pets/`, and local
folders in those locations work too. Its desktop renderer detects v2
sheets by aspect ratio, reads only `spritesheetPath` from `pet.json`,
and plays a compiled-in frame table — the exact counts this atlas uses.
The old `npx petdex hooks` CLI subcommand is retired: agent hooks are
installed from the desktop app's Settings → Agents, one click per agent
(Claude Code, Codex, Gemini CLI, OpenCode, and others). Each installed
hook pipes agent events to `~/.petdex/bin/petdex-hook`, which POSTs to
the app's local server.

That server (`127.0.0.1:7777`) **accepts inbound state pushes**, so any
script can drive the pet directly:

```sh
TOKEN=$(cat ~/.petdex/runtime/update-token)
curl -s -X POST 127.0.0.1:7777/state \
  -H "x-petdex-update-token: $TOKEN" \
  -d '{"state": "jumping", "duration": 3000}'
```

Valid states are exactly this atlas's nine v1 row names (`idle`,
`running`, `running-left`, `running-right`, `waving`, `jumping`,
`failed`, `review`, `waiting`); unknown names get a 400, so the v2 extra
rows are not reachable in petdex — it renders v2 sheets but plays only
rows 1-9. `POST /bubble` shows a speech bubble, and `npx petdex
mcp-server` exposes the same controls as MCP tools (`petdex_set_state`,
`petdex_show_bubble`) for agents that speak MCP.

### Which renderer for custom behavior?

First-party Codex exposes no behavior hooks (tracked upstream in
openai/codex [#20863](https://github.com/openai/codex/issues/20863) and
[#21657](https://github.com/openai/codex/issues/21657)) — until a
first-party contract lands:

- **petdex** is the better target for *pushing* states: an authenticated
  local HTTP API plus an MCP server, multi-agent hook installers, and a
  state vocabulary that matches this atlas row for row.
- **pet-viewer-for-codex** is the better target for *following* Codex
  activity inside VS Code, and it is the only renderer that plays the
  v2 extra rows (via the manifest remapping above). Its file-drop event
  contract is easy to script against but caps out at five derived
  states.

They can coexist with each other and with the first-party overlay.

## Regenerate

```sh
pip install pillow
python3 generate_sprite.py
```

One run writes both packages (`reachy-mini/`, `reachy-mini-v2/`) and
all previews, and fails loudly if any row has the wrong frame count,
non-transparent trailing cells, or art clipped at a cell edge.
