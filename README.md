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
- The `2tnk` muzzle flash plays all 10 HD frames (about twice the stock duration, cosmetic only).
- Audio is classic.
- Rules, weapons, maps and AI are identical to stock Red Alert apart from a written-down list of render-only overrides.

## Changes to shared code

Milestone 1 edits these files that are shared with the Tiberian Dawn HD mod (each is small and generic):

- `OpenRA.Mods.Mobius/Terrain/RemasterTerrain.cs`: `Images` falls back to `Filename`.
- `OpenRA.Mods.Mobius/FileSystem/RemasterFileSystemLoader.cs`: audio manifests are data-driven.
- `OpenRA.Mods.Mobius/Traits/World/RemasterTerrainRenderer.cs`: validation of classic templates.

## Asset Installation

Red Alert HD loads assets directly from an existing digital installation of the C&C Remastered Collection.

#### Windows

Install the C&C Remastered Collection through Steam or Origin.

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
   The mod only accepts an install whose manifest has `"StateFlags" "4"`. Tiberian Dawn HD's
   `1026` (Steam should download the game) is rejected by the content finder.
3. Put the C&C Remastered Collection files in `~/Library/Application Support/Steam/steamapps/common/CnCRemastered`.
   If Steam is installed, restart it and log into an account that owns the collection and it downloads them.
