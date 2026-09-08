# Asset sources & licensing

All models referenced by `ASSET_MANIFEST` in `index.html` are CC0 / permissively licensed:

| Key | Source | License |
|---|---|---|
| `npcCustomer` (fallback CDN) | [three.js examples — RobotExpressive](https://github.com/mrdoob/three.js/tree/r160/examples/models/gltf/RobotExpressive) by Tomás Laulhé | CC0 |
| Optional Kenney drops | [kenney.nl](https://kenney.nl) Food Kit / Furniture Kit | CC0 |
| Optional Quaternius drops | [quaternius.com](https://quaternius.com) | CC0 |

## How to vendor a model

1. Download the pack, pick the `.glb`, and drop it in this folder using the exact
   name from `ASSET_MANIFEST` (e.g. `assets/mug.glb`, `assets/npc_boss.glb`).
2. That's it — the loader prefers `assets/<name>.glb` over the CDN, fits it to the
   prop's physics envelope automatically, and falls back to the procedural builder
   if anything fails to load.
3. Set `scale` / `offset` on the manifest entry if the model needs tuning.

No model in this game may use a license stricter than CC0 without updating this file.
