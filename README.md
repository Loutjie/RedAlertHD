# Red Alert HD

Prototyping repo for OpenRA Red Alert with remastered assets. It is a fork of
[TiberianDawnHD](https://github.com/OpenRA/TiberianDawnHD): the Red Alert mod lives in `mods/ra`
next to the kept Tiberian Dawn reference mod in `mods/cnc`, and packaging builds `ra`.

This repo is made available as a proof of concept demonstrating the capabilities of OpenRA using the C&C Remastered Collection assets.
Performance, memory usage, and loading times have not been optimized, and do not reflect the expected final requirements.

A dedicated GPU is recommended. Use at your own risk.

## Milestone 1 status

Not seen running yet. See [docs/playtest-milestone1.md](docs/playtest-milestone1.md) for the play-test checklist,
the LAN setup against stock OpenRA RA `playtest-20261011`, and the headless checks.

- Only the Temperate tileset is HD. Snow, Interior and Desert maps load with upscaled classic terrain.
- Only the Allied Medium Tank (`2tnk`) is HD. All other units and buildings are upscaled classic art.
- Trees, ore, gems, the ore mine and the building-placement overlay are HD on Temperate (and on Snow, except a few tree husks). Desert and Interior keep classic art for them.
- The `2tnk` muzzle flash plays all 10 HD frames (about twice the stock duration, cosmetic only).
- Audio is classic. The content selector still shows an `AudioStyle` choice, but Red Alert's Remastered audio lists are empty in milestone 1, so choosing `remastered` changes nothing.
- Rules, weapons, maps and AI are identical to stock Red Alert apart from a written-down list of render-only overrides.

## Changes to shared code

Milestone 1 edits these files that are shared with the Tiberian Dawn HD mod (each is small and generic):

- `OpenRA.Mods.Mobius/Terrain/RemasterTerrain.cs`: `Filename` falls back to `Images`.
- `OpenRA.Mods.Mobius/FileSystem/RemasterFileSystemLoader.cs`: audio manifests are data-driven.
- `OpenRA.Mods.Mobius/Traits/World/RemasterTerrainRenderer.cs`: validation of classic templates.

## Asset Installation

Red Alert HD loads assets directly from an existing digital installation of the C&C Remastered Collection.

#### Windows

Install the C&C Remastered Collection through Steam.

#### Linux

Install the C&C Remastered Collection through Steam using the following procedure:

1. Install Steam through your distro package manager or [Flathub](https://flathub.org/apps/details/com.valvesoftware.Steam).
2. Launch Steam and enable "Enable Steam Play for all other titles" from the Settings &rarr; Steam Play menu.
3. Install C&C Remastered Collection from the Library tab.

#### macOS

Install the C&C Remastered Collection through Steam using the following procedure:

1. Make sure that Steam is installed.
2. Create a file `~/Library/Application Support/Steam/steamapps/appmanifest_1213210.acf` with contents
   ```
   "AppState"
   {
   	"appid"		"1213210"
   	"Universe"		"1"
   	"installdir"		"CnCRemastered"
   	"StateFlags"		"4"
   }
   ```
   `"StateFlags" "4"` means "installed". Use it when you place the game files yourself (no Steam
   needed): the mod accepts only an install whose manifest says 4. To have Steam download the game
   instead, use `"StateFlags" "1026"` (Tiberian Dawn HD's value, "download this"); once Steam finishes it
   rewrites the manifest to 4 itself. The mod rejects a manifest that still says 1026.
3. Put the C&C Remastered Collection files in `~/Library/Application Support/Steam/steamapps/common/CnCRemastered`.
   If Steam is installed, restart it and log into an account that owns the collection and it downloads them.
