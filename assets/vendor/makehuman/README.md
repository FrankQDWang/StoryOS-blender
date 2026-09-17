# MakeHuman / MPFB source assets

Selected on 2026-09-17 for the free hand replacement experiment.

- MPFB2 official repository: https://github.com/makehumancommunity/mpfb2
- Pinned source commit: `817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5`.
- Core graphical assets: CC0 1.0, copied verbatim in `LICENSE-CC0.md` from `LICENSE.ASSETS.md` at that revision. MPFB program code is separately GPL; no MPFB code runs or ships in the website.
- `base-human.blend` and `base-human.json`: offline intermediate created with MPFB's core basemesh, macro targets, default rig and supplied skin weights. Creation script: `scripts/prepare_makehuman_base.py`. Original input values are in the JSON. Only arms/hands are extracted for the website.
- Skin: **Aksel Skin**, author **Mindfront**, CC0. Official catalog: https://static.makehumancommunity.org/assets/assetpacks/skins02.html ; original entry: https://www.makehumancommunity.org/node/850 . Pack: https://files.makehumancommunity.org/asset_packs/skins02/skins02_cc0.zip . `mindfront_aksel_skin.mhmat` and `Aksel_Skin_diffuse.png` were extracted byte-for-byte from that pack. No other pack textures are used. The catalog explicitly lists this skin as CC0.

The original skin is kept here for reproducibility. The production GLB contains a rebaked 1024×1024 hand-only atlas, not the full body image. Human topology, UV sampling and original finger weights are retained; the forearm root, sleeves, framing, adaptation and opening motion are project-authored. There was no ready-made book animation in this download.

## Rebuild

Ordinary rebuild needs only Blender and the tracked assets in this folder:

```sh
npm run assets:hands
```

To regenerate the offline base, clone the official MPFB source into the ignored project download directory, check out the exact revision above, and run `scripts/prepare_makehuman_base.py` in Blender with `BLENDER_USER_RESOURCES` set to this project's `downloads/blender-user`. The script redirects MPFB's user directory within that one process; it does not install an add-on globally or save user preferences.
