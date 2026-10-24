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
| `cnc/desert.mix` | absent from RA folders. It is the Tiberian Dawn file `Data/CNCDATA/TIBERIAN_DAWN/CD1/DESERT.MIX` (stock's `cnc95.yaml` installer copies the same `DESERT.MIX`), mounted directly. It holds the `.des` tiles of RA's desert tileset (`p01.des` etc.); without it `--check-missing-sprites` fails the DESERT tileset. |
| `movies` (folder, optional) | not inventoried (movies are `Data/MOVIES_RA.MEG` and `movies1.mix`); out of scope |

All stock names in the table were resolved with the engine's own `MixLoader.MixFile` (handles the
encrypted header and CRC/classic hashes), via a throwaway tool in the scratch directory.

## How `mod.yaml` expresses a nested mount

`FileSystem.Mount(name, explicitName)` is called per `Packages` entry as `key: value`, where `value` is
an optional explicit mount name. `FileSystem.OpenPackage` resolves `explicit|path` by asking the
already-mounted package `explicit` to open `path` as a child package
(`engine/OpenRA.Game/FileSystem/FileSystem.cs`: `TryGetPackageContaining` -> `parent.OpenPackage`).
So mount the outer MIX with an explicit name, then mount children through that name, in order:

Target key: this goes under `FileSystem: RemasterFileSystem` > `ContentSources:` > `<source>:` >
`Packages:` (the key `ContentSourcesFileSystem` reads at `source.Packages` and mounts in order), exactly
like `mods/cnc/mod.yaml` line 52 (`remaster:` source with a `steam` origin, `Mount: data`). It is not
stock RA's `ContentInstallerFileSystem` `ContentPackages` list. `SystemPackages` (mod-provided
folders, `$ra: ra`, `^EngineDir|mods/common: common`) and `OverridePackages` stay separate keys.

```yaml
PackageFormats: Mix, MegV3, ZipFile

# in the remaster content source:
Packages:
	data|Data/CNCDATA/RED_ALERT/CD1/REDALERT.MIX: ra-redalert
	data|Data/CNCDATA/RED_ALERT/CD1/MAIN.MIX: ra-main
	data|Data/CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX: ra-aftermath
	ra-redalert|hires.mix
	ra-redalert|local.mix
	ra-redalert|lores.mix: lores
	ra-redalert|speech.mix
	ra-main|allies.mix
	ra-main|conquer.mix
	ra-main|interior.mix
	ra-main|snow.mix
	ra-main|temperat.mix
	ra-main|russian.mix
	ra-aftermath|sounds.mix
	ra-main|sounds.mix
	~ra-main|scores.mix
	~ra-main|general.mix
	data|Data/CNCDATA/RED_ALERT/CD1/EXPAND2.MIX
	data|Data/CNCDATA/RED_ALERT/CD1/LORES1.MIX
	data|Data/CNCDATA/RED_ALERT/CD1/HIRES1.MIX
	data|Data/CNCDATA/TIBERIAN_DAWN/CD1/DESERT.MIX
	data|Data/CONFIG.MEG
	data|Data/TEXTURES_RA_SRGB.MEG
	data|Data/TEXTURES_COMMON_SRGB.MEG
```

Stock explicit aliases: the only one stock gives a content package is `content|lores.mix: lores`
(`engine/mods/ra/mod.yaml:23`), and stock sequences depend on it (`Filename: lores|atomicon.shp`,
`lores|pbmbicon.shp`, `lores|camicon.shp`, `lores|pinficon.shp` in `engine/mods/ra/sequences/misc.yaml`),
so `ra-redalert|lores.mix: lores` must keep `: lores`. The other aliases in stock are `$ra: ra`,
`common` and `content`, which are system packages/folders, not content MIX files. A grep of
`engine/mods/ra` finds no other `name|` file prefix in use.

Optional mounts: stock marks `~content|movies`, `~content|scores.mix` and `~content|general.mix`
optional (a missing file must not fail loading); the snippet keeps `~` on scores and general. Movies
are not mounted in milestone 1.

Mount order of the two `sounds.mix` files (verified 2026-10-24). The engine resolves a name from the
package mounted last. Every one of the 116 names in the base `CD1/MAIN.MIX > sounds.mix` is also in
Aftermath's `sounds.mix` (142 names). 114 of them are byte-identical, but `dogw6.aud` and `h2obomb2.aud`
differ, and stock uses both (`audio/voices.yaml` dog `Burned`/`Zapped`, `weapons/ballistics.yaml`
`ImpactSounds`). Stock never mounts Aftermath's `sounds.mix`, only the 24 expansion `.aud` files
from it (`content|expand`), so stock plays the base versions. The Aftermath MIX is therefore mounted
**before** the base `sounds.mix`, so the base copy wins every shared name and Aftermath adds only its
26 extra names (the 24 listed above, plus `buzzy1.aud` and `shktrop1.aud`). `ra|bits` and `ra|bits/desert` in stock are mod-provided system
packages mounted after content so they can override it; they are not Remastered content and need no
inventory entry.

The explicit names (`ra-redalert`, `ra-main`, `ra-aftermath`) are chosen here; any unused names work.
`PackageFormats` must include `Mix` (stock RA has only `Mix`) and `MegV3`, `ZipFile` for the HD
archives, as `mods/cnc/mod.yaml` does (`Mix, MegV3, ZipFile, ISO9660`). Nested MIX children are
located by filename hash, so the lower-case stock names above resolve. The same-named top-level `MAIN.MIX`
files in the three folders must not share an explicit name.

Name resolution relies on `engine/global mix database.dat`, which is mounted through the `^EngineDir`
system package. Without it the outer and nested MIX files report no contents, and every nested mount fails.
`ContentSourcesFileSystem.Mount` swallows per-package mount exceptions, so a broken package path shows
up only as missing sprites in `--check-missing-sprites`, not as a load error.

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

## HD Temperate tileset

`mods/ra/tilesets/temperat.yaml` is stock `engine/mods/ra/tilesets/temperat.yaml` with
`SheetSize: 1024` renamed to `IndexedSheetSize: 1024` (the `RemasterTerrain` field TD HD uses),
then converted:

```sh
./utility.sh --convert-tileset "$PWD/mods/ra/tilesets/temperat.yaml" \
	"<install>/Data/CONFIG.MEG" RA_TERRAIN_TEMPERATE.XML
```

- **Pass an absolute tileset path.** `utility.sh` changes into `engine/` before it runs, so a relative
  `mods/ra/tilesets/temperat.yaml` resolves to the stock engine file and converts that in place.
- The converter renames `Images` to `Filename` and adds `RemasteredFilenames` (shape index to
  `DATA\ART\TEXTURES\SRGB\RED_ALERT\TERRAIN\TEMPERATE\...DDS` names). It needed no RA changes.
- `python3 tools/check_tileset_parity.py` (part of `make test`) asserts that General (except the sheet
  size field), the Terrain section, MultiBrushCollections and every template's Id, Size, Tiles,
  Categories and PickAny equal stock. `-v` lists the classic-only templates.
- Coverage: 257 of 308 templates have Remastered art for every tile in `Tiles`. None is partial.
- **51 templates have no Remastered counterpart** and keep classic art (upscaled under
  `ArtworkStyle: remastered`). Their names do not occur anywhere in `RA_TERRAIN_TEMPERATE.XML`:
  - shore `sh57`..`sh64` (Ids 500, 502..508)
  - small bridges `sbridge1/2/3/4` with `h`, `d` and `x` variants (Ids 519..534)
  - `sccnr`, `sccnl`, `sccsr`, `sccsl`, `sccln`, `sccls`, `sccrn`, `sccrs` (Ids 550..557)
  - `deca`..`dech` decorations (Ids 580..588; `decc` is used twice)
  - `fjord1`, `fjord2` (Ids 590, 591)
  - `cliffsl1`..`cliffsl4`, `cliffsw1`..`cliffsw4` (Ids 401..408)
- The Remastered XML has frames for some shape indices that are absent from stock `Tiles` (for
  example templates 131, 235, 380, 382 and 383). They are reserved but never drawn, because maps
  cannot reference a tile index that is not in `Tiles`.

## `2tnk` (Medium Tank) body and turret

Archive: `DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\2TNK.ZIP` in `TEXTURES_RA_SRGB.MEG`.

- Members: `2tnk-0000.tga` .. `2tnk-0063.tga` plus a matching `2tnk-NNNN.meta` each: 64 frames
  (128 members), all frames have both files.
- **Verified layout: Remastered frame N is classic `2tnk.shp` shape N, for N = 0..63.** Source: the
  Remastered game's own shape table `DATA\XML\TILESETS\RA_UNITS.XML` (in `CONFIG.MEG`) has 64 `2TNK`
  tiles, and the tile with `<Shape>N</Shape>` lists exactly one frame, `2tnk\2tnk-NNNN.tga`.
  `TD_UNITS.XML` maps `MTNK` the same way, which is why TD HD's `mtnk` override needs no
  `RemasteredStart`/`RemasteredLength`.
- So the stock indexing carries over unchanged: body `idle` = frames 0..31, `turret` = `Start: 32`,
  32 facings, both with stock `UseClassicFacings: True`. No `RemasteredStart`, `RemasteredLength`
  or per-facing `RemasteredOffset` is needed. Visual spot check (TGAs converted to PNG in scratch):
  frame 0 faces north, frame 8 is side-on and turret frame 40 points its barrel left, so the order is
  counter-clockwise from north, as in classic Westwood shapes and as in `MTNK.ZIP`.
- Per-frame placement comes from the `.meta` files, which the engine applies itself.
  They are JSON `{"size":[192,192],"crop":[left,top,right,bottom]}`. `ShpRemasteredLoader` reads
  them as `Rectangle.FromLTRB`, and each cropped TGA is placed inside its frame canvas. All 64 frames
  share one 192x192 canvas (body and turret alike, as in `MTNK.ZIP`), so the turret stays registered
  on the hull without sequence offsets. The 2TNK body crops equal MTNK's on the sampled frames
  (0, 8, 16, 31).
- **No separate husk archive** for 2tnk: nothing matching `2TNK*`, `*HUSK*` or `*DESTROYED*` exists in
  `TEXTURES_RA_SRGB.MEG`. `2tnk.destroyed` reuses `2TNK.ZIP` (as `mtnk.destroyed` reuses
  `MTNK.ZIP` in `mods/cnc`), keeping the stock `ZOffset: -512`.
- `TEXTURES_PATCHES_SRGB.MEG` and `TEXTURES_COMMON_SRGB.MEG` contain no `2TNK` or `GUNFIRE` entries, so
  nothing patches these archives.

## Muzzle flash

Stock RA's `2tnk` `muzzle` sequence (`engine/mods/ra/sequences/vehicles.yaml`) uses
`Filename: gunfire2.shp`, `Length: 5`. `gunfire2.shp` is an OpenRA file in `engine/mods/ra/bits`
(5 frames, 16x16), not a Westwood original. The Remastered equivalent is
`DATA\ART\TEXTURES\SRGB\RED_ALERT\VFX\GUNFIRE.ZIP`. `RA_VFX.XML` has only one gun-flash entry,
`GUNFIRE`, and no `GUNFIRE2`.

- Members: `gunfire-0000.tga` .. `gunfire-0009.tga` = 10 frames; `.meta` files exist only for frames
  0, 1, 3, 4, 5, 6 and 9 (frames 2, 7 and 8 are uncropped 85x85 TGAs, which the loader accepts).
  `RA_VFX.XML` maps `GUNFIRE` shapes 0..9 one-to-one to these frames.
- **The 10 frames are one continuous animation, not two variants and not doubled frames.** The flash
  grows over frames 0..2, then turns to smoke that fades over frames 3..9 (visual check).
- The RA archive is byte-identical to TD's `TIBERIAN_DAWN\VFX\GUNFIRE.ZIP`. TD HD's `mtnk` muzzle
  plays all 10 frames, because stock TD declares `Length: *` and `RemasterSpriteSequence` inherits it.
  Stock RA's `Length: 5` would cut the HD animation off after two smoke frames, so the RA override
  sets `RemasteredLength: *` to play all 10, as TD HD does. Muzzle overlays are render-only
  (`WithMuzzleOverlay`), so this does not affect rules parity.

## Reproduce

Scratch tooling (not committed): a small .NET console referencing `engine/bin/OpenRA.Game.dll` and
`OpenRA.Mods.Cnc.dll` opened each MIX with `MixLoader.MixFile(stream, name, candidateNames)`; a
Python MEG v3 reader (header `<6I`, names table, then 20-byte records `<HIIIIH`) listed
`TEXTURES_RA_SRGB.MEG` and `CONFIG.MEG` and read ZIP member names in memory. For the 2tnk and muzzle
layout, the same reader extracted the two ZIPs and `RA_UNITS.XML`/`RA_VFX.XML` to a scratch directory
outside the repo. A Python `xml.etree` pass then listed each `<Tile>`'s `Name`, `Shape` and `Frame`.

## Headless checks

`OpenRA.Utility` mounts Remastered content only if the support-dir `settings.yaml` has a
`ContentSource@ra` node. This is the node the in-game source selector writes. The utility takes no
`Key=Value` settings overrides (`Game.InitializeSettings(Arguments.Empty)`). On macOS, both the support
dir (`~/Library/Application Support/OpenRA`) and the Steam lookup
(`~/Library/Application Support/Steam`) come from `$HOME`. So run the utility with `HOME` set to a
scratch directory that holds a settings file and a Steam folder pointing at the real install.
This never writes to the real support dir or the Steam folder:

```sh
H=/private/tmp/claude-501/rahd-scratch/home-content     # any scratch path
STEAM="$HOME/Library/Application Support/Steam"
mkdir -p "$H/Library/Application Support/OpenRA" "$H/Library/Application Support/Steam/steamapps/common"
printf 'ContentSource@ra:\n\tContentSource: remaster\n\tArtworkStyle: remastered\n\tAudioStyle: classic\n' \
	> "$H/Library/Application Support/OpenRA/settings.yaml"
printf '"AppState"\n{\n\t"appid"\t\t"1213210"\n\t"StateFlags"\t\t"4"\n\t"installdir"\t\t"CnCRemastered"\n}\n' \
	> "$H/Library/Application Support/Steam/steamapps/appmanifest_1213210.acf"
ln -sfn "$STEAM/steamapps/common/CnCRemastered" "$H/Library/Application Support/Steam/steamapps/common/CnCRemastered"

HOME="$H" ./utility.sh --check-missing-sprites    # exit 0 = every classic and HD sprite resolves
HOME="$H" ./utility.sh --check-yaml
```

- `ArtworkStyle: classic` in that settings file checks the classic-art path instead (no terrain upscale).
- Why the scratch app manifest: `SteamContentOrigin` accepts an install only if its
  `appmanifest_1213210.acf` has `"StateFlags" "4"` (fully installed). The manifest on this Mac is a
  66-byte stub with only `appid` and `installdir`, so the real one is rejected. That also means the
  in-game source selector will report no source until `"StateFlags"		"4"` is added to the real
  manifest. Steam itself is not installed here, so nothing else writes that file.
- **Missing install:** point `HOME` at an empty directory: `HOME=<empty dir> ./utility.sh --check-yaml`.
  With no settings and no Steam folder, it exits 0 with no errors. `--check-missing-sprites` then
  fails with `blank.png not found`, the expected "no content mounted" result.
- The same pattern works for Tiberian Dawn HD (`Mod=cnc`). Its settings node is `ContentSource@cnc`
  with `ArtworkStyle`, `AudioLanguage`, `AudioStyle` and `MusicStyle`.
