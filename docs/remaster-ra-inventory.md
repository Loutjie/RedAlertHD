# Remastered Collection inventory for Red Alert (milestone 1)

Paths and frame layouts only. No game data is stored here. Verified 2026-10-24 against Steam AppId
`1213210` (`CnCRemastered`). All paths are relative to the install root, i.e. the `data` mount that
`SteamContentOrigin` provides (`Mount: data`, same as `mods/cnc/mod.yaml`).

## Install layout

Classic RA MIX files live in `Data/CNCDATA/RED_ALERT/{CD1,COUNTERSTRIKE,AFTERMATH}/`. `CD1` is the
base game. Each folder holds `MAIN.MIX`, `REDALERT.MIX`, `EXPAND.MIX`, `EXPAND2.MIX`, `HIRES1.MIX`,
`LORES1.MIX` and `REDALERT.INI`. The four `EXPAND*/HIRES1/LORES1` files are byte-size identical in all
three folders (458242, 469922, 90264, 57076 bytes), so mount them from `CD1`.

Stock RA content files are nested inside two outer MIX files, not loose:

| Outer MIX (CD1) | Nested files found |
| --- | --- |
| `REDALERT.MIX` | `hires.mix`, `local.mix`, `lores.mix`, `speech.mix` |
| `MAIN.MIX` | `allies.mix`, `conquer.mix`, `general.mix`, `interior.mix`, `movies1.mix`, `russian.mix`, `scores.mix`, `snow.mix`, `sounds.mix`, `temperat.mix` |

This matches the Steam Ultimate Collection layout in `engine/mods/ra-content/installer/steam.yaml`
(`REDALERT.MIX` and `MAIN1.MIX` there), with `MAIN.MIX` as the Remastered name.
`movies2.mix` is not in `CD1/MAIN.MIX`. `AFTERMATH/MAIN.MIX` and `COUNTERSTRIKE/MAIN.MIX` also carry
`allies/conquer/interior/russian/scores/snow/sounds/temperat/general.mix`, plus `edhi.mix`, `edlo.mix`
and a `local mix database.dat`; the base game does not need them.

## Stock `ContentPackages` entry -> where it lives

| Stock entry | Remastered location |
| --- | --- |
| `allies.mix` | `Data/CNCDATA/RED_ALERT/CD1/MAIN.MIX` > `allies.mix` |
| `conquer.mix` | `CD1/MAIN.MIX` > `conquer.mix` |
| `interior.mix` | `CD1/MAIN.MIX` > `interior.mix` |
| `snow.mix` | `CD1/MAIN.MIX` > `snow.mix` |
| `temperat.mix` | `CD1/MAIN.MIX` > `temperat.mix` |
| `russian.mix` | `CD1/MAIN.MIX` > `russian.mix` |
| `sounds.mix` | `CD1/MAIN.MIX` > `sounds.mix` |
| `scores.mix` | `CD1/MAIN.MIX` > `scores.mix` |
| `general.mix` | `CD1/MAIN.MIX` > `general.mix` |
| `hires.mix` | `CD1/REDALERT.MIX` > `hires.mix` |
| `local.mix` | `CD1/REDALERT.MIX` > `local.mix` |
| `lores.mix` | `CD1/REDALERT.MIX` > `lores.mix` |
| `speech.mix` | `CD1/REDALERT.MIX` > `speech.mix` |
| `expand/expand2.mix` | loose file `Data/CNCDATA/RED_ALERT/CD1/EXPAND2.MIX` |
| `expand/lores1.mix` | loose file `Data/CNCDATA/RED_ALERT/CD1/LORES1.MIX` |
| `expand/hires1.mix` | loose file `Data/CNCDATA/RED_ALERT/CD1/HIRES1.MIX` |
| `expand/*.aud` (24 files: `chrotnk1`, `fixit1`, `jburn1`, `jchrge1`, `jcrisp1`, `jdance1`, `jjuice1`, `jjump1`, `jlight1`, `jpower1`, `jshock1`, `jyes1`, `madchrg2`, `madexplo`, `mboss1`, `mhear1`, `mhotdig1`, `mhowdy1`, `mhuh1`, `mlaff1`, `mrise1`, `mwrench1`, `myeehaw1`, `myes1`) | all 24 found inside `Data/CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX` > `sounds.mix` (Aftermath's sounds MIX). `COUNTERSTRIKE/MAIN.MIX` > `sounds.mix` has none of them. Stock extracts this nested MIX to `expand/sounds-aftermath.mix`. |
| `expand` (folder) | no folder; `EXPAND.MIX` (CD1) exists but is not in the stock list and no name from the list resolved in it |
| `cnc/desert.mix` | **absent from RA folders**. It is a Tiberian Dawn file: `Data/CNCDATA/TIBERIAN_DAWN/CD1/DESERT.MIX`. Not needed for Temperate-only milestone 1. |
| `movies` (folder, optional) | not inventoried (movies are `Data/MOVIES_RA.MEG` and `movies1.mix`); out of scope |

All stock names in the table were resolved with the engine's own `MixLoader.MixFile` (handles the
encrypted header and CRC/classic hashes), via a throwaway tool in the scratch directory.

## How `mod.yaml` expresses a nested mount

`FileSystem.Mount(name, explicitName)` is called per `Packages` entry as `key: value`, where `value` is
an optional explicit mount name. `FileSystem.OpenPackage` resolves `explicit|path` by asking the
already-mounted package `explicit` to open `path` as a child package
(`engine/OpenRA.Game/FileSystem/FileSystem.cs`: `TryGetPackageContaining` -> `parent.OpenPackage`).
So mount the outer MIX with an explicit name, then mount children through that name, in order:

```yaml
PackageFormats: Mix, MegV3, ZipFile

# in the remaster content source:
Packages:
	data|Data/CNCDATA/RED_ALERT/CD1/REDALERT.MIX: ra-redalert
	data|Data/CNCDATA/RED_ALERT/CD1/MAIN.MIX: ra-main
	data|Data/CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX: ra-aftermath
	ra-redalert|hires.mix
	ra-redalert|local.mix
	ra-redalert|lores.mix
	ra-redalert|speech.mix
	ra-main|allies.mix
	ra-main|conquer.mix
	ra-main|interior.mix
	ra-main|snow.mix
	ra-main|temperat.mix
	ra-main|russian.mix
	ra-main|sounds.mix
	ra-main|scores.mix
	ra-main|general.mix
	data|Data/CNCDATA/RED_ALERT/CD1/EXPAND2.MIX
	data|Data/CNCDATA/RED_ALERT/CD1/LORES1.MIX
	data|Data/CNCDATA/RED_ALERT/CD1/HIRES1.MIX
	ra-aftermath|sounds.mix
	data|Data/CONFIG.MEG
	data|Data/TEXTURES_RA_SRGB.MEG
	data|Data/TEXTURES_COMMON_SRGB.MEG
```

The explicit names (`ra-redalert`, `ra-main`, `ra-aftermath`) are chosen here; any unused names work.
`PackageFormats` must include `Mix` (stock RA has only `Mix`) and `MegV3`, `ZipFile` for the HD
archives, as `mods/cnc/mod.yaml` does (`Mix, MegV3, ZipFile, ISO9660`). Nested MIX children are
located by filename hash, so the lower-case stock names above resolve. Points to verify when the mod
loads: the Aftermath `sounds.mix` mounted last may shadow names also present in the base `sounds.mix`
(the 24 `.aud` names are expansion-only in stock), and the same-named top-level `MAIN.MIX` files in
three folders must not share an explicit name.

Remastered artwork is addressed in sequences with `RemasteredFilename:` using the in-MEG path, as in
`mods/cnc/sequences/vehicles-overrides.yaml`.

## Remastered archives

- `Data/CONFIG.MEG` (MEG v3, 3974 files) holds `DATA\XML\TILESETS.XML` and per-set XML under
  `DATA\XML\TILESETS\`: `RA_TERRAIN_TEMPERATE.XML`, `RA_TERRAIN_SNOW.XML`, `RA_TERRAIN_INTERIOR.XML`,
  `RA_TERRAIN_SHROUD.XML`, `RA_RADARMAP.XML`, `RA_STRUCTURES.XML`, `RA_UNITS.XML`, `RA_VFX.XML`.
  **RA Temperate XML: `DATA\XML\TILESETS\RA_TERRAIN_TEMPERATE.XML`.**
  `--convert-tileset` (`RemasterTilesetConverter`) takes `CONFIG.MEG` and the bare name, so pass
  `RA_TERRAIN_TEMPERATE.XML` (it prefixes `DATA\XML\TILESETS\` itself).
- `Data/TEXTURES_RA_SRGB.MEG` (MEG v3, 17330 files) holds RA art under
  `DATA\ART\TEXTURES\SRGB\RED_ALERT\{UNITS,VFX,TERRAIN\<SET>,...}`. Terrain tiles are DDS under
  `...\RED_ALERT\TERRAIN\<TEMPERATE|SNOW|INTERIOR>\<TILE>\<TILE>-NNNN.DDS`.
- Also present: `TEXTURES_COMMON_SRGB.MEG`, `TEXTURES_PATCHES_SRGB.MEG`, `TEXTURES_SRGB.MEG`,
  `MUSIC.MEG`, `SFX2D_*.MEG`, `SFX3D.MEG`, `MOVIES_RA.MEG`.

## `2tnk` (Medium Tank) body and turret

Archive: `DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\2TNK.ZIP` in `TEXTURES_RA_SRGB.MEG`.

- Members: `2tnk-0000.tga` .. `2tnk-0063.tga` plus a matching `2tnk-NNNN.meta` each: 64 frames
  (128 members), all frames have both files.
- Layout, from naming and by analogy with the stock sprite (`2tnk.shp`: `idle` 32 facings, `turret`
  `Start: 32`, 32 facings) and `1TNK.ZIP` (same 0..63 naming): **body = frames 0..31, turret = frames
  32..63**, so `RemasteredStart: 0` / `RemasteredLength: 32` for body and `32` / `32` for turret.
  The `.meta` files are JSON `{"size":[192,192],"crop":[x,y,w,h]}`; the body and turret share a
  192x192 canvas (spot checks on frames 0 and 32).
- **No separate husk archive** for 2tnk: nothing matching `2TNK*`, `*HUSK*` or `*DESTROYED*` exists in
  `TEXTURES_RA_SRGB.MEG`. `2tnk.destroyed` must reuse `2TNK.ZIP` (as `mtnk.destroyed` reuses
  `MTNK.ZIP` in `mods/cnc`).
- Not verified here: whether frame 0 faces north and the direction of rotation match the stock
  facing order; the TD `MTNK.ZIP` convention is the reference when wiring sequences.

## Muzzle flash

Stock RA's `2tnk` `muzzle` sequence (`engine/mods/ra/sequences/vehicles.yaml`) uses
`Filename: gunfire2.shp`, `Length: 5`. The Remastered equivalent is the RA VFX archive
`DATA\ART\TEXTURES\SRGB\RED_ALERT\VFX\GUNFIRE.ZIP` (there is no `GUNFIRE2` in the RA VFX list).

- Members: `gunfire-0000.tga` .. `gunfire-0009.tga` = 10 frames; `.meta` files exist only for frames
  0, 1, 3, 4, 5, 6 and 9 (frames 2, 7 and 8 have a `.tga` but no `.meta`).
- Frame 0 canvas is 85x85. Remastered frame count (10) differs from the stock sequence length (5), so
  the muzzle override will need an explicit `RemasteredLength`/`RemasteredStart` choice. TD's
  `mtnk` muzzle (`TIBERIAN_DAWN\VFX\GUNFIRE.ZIP`) is the precedent for a `muzzle` override.

## Reproduce

Scratch tooling (not committed): a small .NET console referencing `engine/bin/OpenRA.Game.dll` and
`OpenRA.Mods.Cnc.dll` opened each MIX with `MixLoader.MixFile(stream, name, candidateNames)`; a
Python MEG v3 reader (header `<6I`, names table, then 20-byte records `<HIIIIH`) listed
`TEXTURES_RA_SRGB.MEG` and `CONFIG.MEG` and read ZIP member names in memory.
