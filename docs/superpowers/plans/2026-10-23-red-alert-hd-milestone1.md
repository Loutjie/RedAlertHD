# Red Alert HD Milestone 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `ra` mod in this repo that runs OpenRA Red Alert from the user's Remastered Collection install, draws Temperate terrain and the Allied Medium Tank (`2tnk`) in HD, shows everything else as upscaled classic art, and stays multiplayer-compatible with stock OpenRA RA `playtest-20261011`.

**Architecture:** Mirror TiberianDawnHD's `mods/cnc` overlay pattern for Red Alert: a new `mods/ra` that pulls every rules/weapons/map file unchanged from the engine's `ra|` package and overlays only HD sequences, a converted Temperate tileset, render-only rules overrides, and Remastered content sources. Existing shared C# (`OpenRA.Mods.Mobius`) is reused; the existing `mods/cnc` stays as a buildable reference. Two headless checks make the anti-goals testable: rules parity with stock RA, and no missing sprites.

**Tech Stack:** OpenRA engine `playtest-20261011`, .NET 10, MiniYaml, C# (only if needed), Python 3 stdlib for the parity script.

**Spec:** `docs/superpowers/specs/2026-10-23-red-alert-hd-milestone1-design.md`

## Global Constraints

- Engine `ENGINE_VERSION="playtest-20261011"` (unchanged in `mod.config`).
- Mod ID `ra`; `Metadata.Version: {DEV_VERSION}`; `SupportsMapsFrom: ra`; `PACKAGING_OVERWRITE_MOD_VERSION="True"` kept.
- Rules, weapons, maps, AI identical to stock RA except entries in the render-only allow-list (Task 3).
- Never commit, copy or redistribute any original/Remastered game file or derived art (MIX, MEG, ZIP/TGA/DDS frames, XML, audio). YAML naming files/frames is fine.
- Remastered install location on this Mac: `~/Library/Application Support/Steam/steamapps/common/CnCRemastered`, found through `steamapps/appmanifest_1213210.acf` (AppId `1213210`).
- `.editorconfig` style; `make check` and `make TREAT_WARNINGS_AS_ERRORS=true test` must pass.
- RA-specific C# goes in new files; edits to existing Mobius files only if small and generic, each listed in the PR description.
- Do not modify `mods/cnc` or `mods/remaster-content`.
- Never launch the game. Headless `./utility.sh` commands are fine.
- Commits: repo-local identity Loutjie Coetzee <lccoetzee@gmail.com>; trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. No push/PR without the user's go-ahead.
- Milestone 1 lists only the Temperate tileset; Snow/Interior/Desert maps are unsupported until milestone 2 (spec non-goal).

## Review Focus

1. **Install missing or incomplete** → the mod must fall back to the content-selector prompt, not crash on boot. Task 4 checks `--check-yaml` with the manifest renamed away.
2. **A stock RA map that places actors or templates the HD tileset lacks** → the tile/sprite falls back to upscaled classic art, never invisible. Task 7's `--check-missing-sprites` run must be clean, and Task 5 records any unmapped templates.
3. **A stock RA map on a tileset other than Temperate selected in the lobby** → it shows as unavailable rather than crashing. Task 2 verifies the Temperate-only `TileSets` list loads.
4. **A rules override that silently changes gameplay** (e.g. a trait added with a non-render field) → the parity check fails. Task 3 has a negative test.
5. **The `2tnk` turret or husk misaligned at some facings** → per-facing offsets come from the Remastered frame layout, not guesses. Task 6 records the frame layout in the inventory and the play-test checklist covers all 32 facings.

---

### Task 1: Remastered inventory (requires the install)

**Files:**
- Create: `docs/remaster-ra-inventory.md`

**Interfaces:**
- Produces: the exact paths later tasks use. Classic RA MIX packages inside the install, relative to the install root (e.g. under `Data/CNCDATA/RED_ALERT/`). The config MEG that holds `DATA\XML\TILESETS\*.XML`, and the RA Temperate XML name inside it. The `2tnk` body+turret archive inside `TEXTURES_RA_SRGB.MEG` (expected near `DATA\ART\TEXTURES\SRGB\RED_ALERT\UNITS\2TNK.ZIP`), with frame count and the body/turret frame ranges. The RA muzzle-flash archive (gunfire2 equivalent). Whether a separate husk archive exists.

- [ ] **Step 1: Confirm the install is present**

Run: `ls "$HOME/Library/Application Support/Steam/steamapps/appmanifest_1213210.acf" "$HOME/Library/Application Support/Steam/steamapps/common/CnCRemastered/Data"`
Expected: both exist. If not, stop and report BLOCKED: the user is copying the files there.

- [ ] **Step 2: List RA classic packages and Remastered archives**

Use read-only listing only. Options are `find` for MIX files, the engine's MEG reader via `./utility.sh` package listing or `--extract` into a scratch dir outside the repo, or a throwaway script in the scratchpad. Nothing extracted may be written inside the repo.

- [ ] **Step 3: Write `docs/remaster-ra-inventory.md`**

Record paths and frame layouts only, no image data. Add one line per RA classic MIX that matches an entry in stock RA's `ContentPackages` list (`allies.mix`, `conquer.mix`, `interior.mix`, `lores.mix`, `hires.mix`, `local.mix`, `russian.mix`, `snow.mix`, `sounds.mix`, `speech.mix`, `temperat.mix`, `expand2.mix`, `lores1.mix`, `hires1.mix`, `scores.mix`, `general.mix`, the expand `.aud` set), giving where it lives in the Remastered install or that it is absent. Note that stock RA's `content|cnc/desert.mix` is a TD file.

- [ ] **Step 4: Commit**

```bash
git add docs/remaster-ra-inventory.md
git commit -m "Record Remastered Collection paths for Red Alert"
```

### Task 2: `ra` mod scaffold that loads stock RA content

**Files:**
- Create: `mods/ra/mod.yaml`, `mods/ra/rules/overrides.yaml`, `mods/ra/bits/` (copy `blank.png` from `mods/cnc/bits` if the terrain needs it), `mods/ra-remaster-content/mod.yaml`, `mods/ra-remaster-content/prompt.yaml`, `mods/ra-remaster-content/prompt.ftl`
- Modify: `mod.config` (`MOD_ID="ra"`), `Makefile` and `make.ps1` (`test` checks `ra-remaster-content` instead of `remaster-content`)

**Interfaces:**
- Consumes: Task 1 inventory (MIX paths).
- Produces: package aliases used by later tasks. `ra` = engine `mods/ra`. `rahd` = this repo's `mods/ra` (`$ra: rahd`). `data` = the Remastered install mount. The selector mod id is `ra-remaster-content`.

- [ ] **Step 1: Write `mods/ra/mod.yaml`**

Start from the engine's `mods/ra/mod.yaml` at `playtest-20261011`. Keep `Rules`, `Weapons`, `Voices`, `Notifications`, `Music`, `Missions`, `MapFolders` and `ChromeLayout` lists byte-for-byte as `ra|…`. Append `rahd|rules/overrides.yaml` as the last `Rules` entry. Then apply the TD HD deltas, copied from `mods/cnc/mod.yaml`:
- `PackageFormats: Mix, MegV3, ZipFile`;
- `FileSystem: RemasterFileSystem` with `SystemPackages` (`^EngineDir`, `$ra: rahd`, `^EngineDir|mods/ra: ra`, `^EngineDir|mods/common: common`, scripts/uibits);
- `OverridePackages` (`ra|bits`, `ra|bits/desert`, `rahd|bits`);
- `SourceSelectorMod: ra-remaster-content`;
- `ContentSources.remaster` with the Steam origin (AppId 1213210, `Mount: data`) and `Packages` from the Task 1 inventory, plus `data|Data/TEXTURES_RA_SRGB.MEG` and `data|Data/TEXTURES_COMMON_SRGB.MEG`;
- `Assemblies` add `OpenRA.Mods.Mobius.dll`;
- `MapGrid: TileSize: 128,128`, `Type: Rectangular`, `EnableFrameBufferDownscale: true`;
- `WorldViewportSizes.DefaultScale: 0.1875`;
- `SpriteFormats` add `Tga, ShpRemastered, Dds, PngSheet`;
- `TerrainFormat: RemasterTerrain`;
- `SpriteSequenceFormat: RemasterSpriteSequence` with `BgraSheetSize: 8192`, `IndexedSheetSize: 512`.

For `TileSets`, list only Temperate for now. Task 5 replaces it with the HD file; until then use `ra|tilesets/temperat.yaml` if `RemasterTerrain` accepts a classic tileset with `UseRemasteredTerrain` false, otherwise defer the `TileSets` entry to Task 5 and note it in the report.

- [ ] **Step 2: Write `mods/ra/rules/overrides.yaml`**

```yaml
^BaseWorld:
	-TerrainRenderer:
	RemasterTerrainRenderer:
```

Confirm `^BaseWorld` and `TerrainRenderer` exist in engine `mods/ra/rules/world.yaml`. If RA uses a different key, use the RA key and note it.

- [ ] **Step 3: Write `mods/ra-remaster-content/*`**

Copy `mods/remaster-content/*`, retarget it (`Mod: ra`, RA attributes and origins only: the Remastered Steam origin, artwork/audio style options), and point UI images at `ra|uibits`. Write all text through the existing `.ftl` keys pattern.

- [ ] **Step 4: Update `mod.config`, `Makefile`, `make.ps1`**

Set `MOD_ID="ra"`. The `test` target's second check becomes `Mod=ra-remaster-content ./utility.sh --check-yaml`. Make the equivalent change in `make.ps1`.

- [ ] **Step 5: Verify**

Run: `make check && make TREAT_WARNINGS_AS_ERRORS=true test`
Expected: build succeeds; both `--check-yaml` runs report no errors.

- [ ] **Step 6: Commit**

```bash
git add mods/ra mods/ra-remaster-content mod.config Makefile make.ps1
git commit -m "Add Red Alert HD mod scaffold on Remastered content"
```

### Task 3: Rules-parity check (multiplayer guard)

**Files:**
- Create: `tools/check_rules_parity.py`, `mods/ra/render-only-overrides.txt`
- Modify: `Makefile` and `make.ps1` (`test` runs the script)

**Interfaces:**
- Consumes: Task 2 mod (`./utility.sh` runs `ra`), engine checkout at `./engine`.
- Produces: `python3 tools/check_rules_parity.py`, which exits 0 iff, for every actor and weapon defined by stock RA, the resolved MiniYaml from this mod equals stock RA's. Before comparing, it removes from both sides the trait or field keys listed in `render-only-overrides.txt`. It prints each differing actor/weapon and key, and exits 1 on any difference.

Allow-list format, one entry per line: `<ACTOR or ^ABSTRACT>:<TraitKey>[.<Field>]  # reason it cannot affect sync`. Initial entries: `World:TerrainRenderer` and `World:RemasterTerrainRenderer`, with reasons. Get stock output from the engine's own utility (`cd engine && ./utility.sh ra --resolved-rules <ACTOR>` / `--resolved-weapons <WEAPON>`) and this mod's from `./utility.sh --resolved-rules <ACTOR>`. Take actor and weapon names from top-level keys in the engine's `mods/ra/rules/*.yaml` and `weapons/*.yaml`, skipping `^` abstracts. Also compare the `Rules`, `Weapons` and `Missions` lists of the two `mod.yaml`s: identical, except the trailing `rahd|rules/overrides.yaml`.

- [ ] **Step 1: Write the script and the allow-list**

- [ ] **Step 2: Run it on the scaffold**

Run: `python3 tools/check_rules_parity.py`
Expected: `parity OK` and exit 0.

- [ ] **Step 3: Negative test**

Temporarily add `2TNK:\n\tMobile:\n\t\tSpeed: 1` to `mods/ra/rules/overrides.yaml`, then run the script.
Expected: exit 1 and output naming `2TNK` `Mobile.Speed`. Revert the edit and confirm the script exits 0 again.

- [ ] **Step 4: Wire into `make test` and `make.ps1 test`; run `make TREAT_WARNINGS_AS_ERRORS=true test`**

Expected: passes.

- [ ] **Step 5: Commit**

```bash
git add tools/check_rules_parity.py mods/ra/render-only-overrides.txt Makefile make.ps1
git commit -m "Check Red Alert HD rules stay identical to stock Red Alert"
```

### Task 4: Content loading from the install

**Files:**
- Modify: `mods/ra/mod.yaml` (`ContentSources`, if Task 2 used placeholders), `docs/remaster-ra-inventory.md` (fix anything found wrong)

**Interfaces:**
- Consumes: Task 1 inventory, Task 2 scaffold.
- Produces: a mod that mounts the classic RA MIX files and the RA texture MEGs from the install.

- [ ] **Step 1: Run the sprite check with the install present**

Run: `./utility.sh --check-missing-sprites`
Expected: before HD mapping, the only failures are tileset templates (fixed in Task 5) or none. No failures should come from classic unit or building sprites. Each one that does is a wrong or missing package path; fix `ContentSources.Packages`.

- [ ] **Step 2: Missing-install behaviour**

Temporarily rename `appmanifest_1213210.acf`, then run `./utility.sh --check-yaml`.
Expected: no crash. YAML check passes. Restore the file.

- [ ] **Step 3: Commit**

```bash
git add mods/ra/mod.yaml docs/remaster-ra-inventory.md
git commit -m "Mount Red Alert classic and Remastered packages from the install"
```

### Task 5: HD Temperate tileset

**Files:**
- Create: `mods/ra/tilesets/temperat.yaml` (generated, then committed)
- Modify: `mods/ra/mod.yaml` (`TileSets: rahd|tilesets/temperat.yaml`)

**Interfaces:**
- Consumes: Task 1 (config MEG path, RA Temperate XML name), the existing `--convert-tileset FILENAME CONFIG.MEG TERRAIN-XML` command in `OpenRA.Mods.Mobius/UtilityCommands/RemasterTilesetConverter.cs`.
- Produces: an HD Temperate tileset whose template IDs and terrain types equal stock `ra|tilesets/temperat.yaml`.

- [ ] **Step 1: Generate**

Copy engine `mods/ra/tilesets/temperat.yaml` to `mods/ra/tilesets/temperat.yaml`, add the `RemasterTerrain` header fields TD HD's `mods/cnc/tilesets/temperat.yaml` uses, then run `./utility.sh --convert-tileset mods/ra/tilesets/temperat.yaml "<install>/<config MEG>" <RA temperate XML>`.

If the converter needs changes for RA (XML naming, template code mapping, the `TmpRA` format), make them as small generic edits and list them in the report.

- [ ] **Step 2: Verify template parity**

Assert with a short script or diff that every template `Id`, `Size` and `Tiles` terrain type in the generated file equals the stock file. Terrain types affect pathing, so this is a sync requirement, not a cosmetic one. Write templates with no Remastered counterpart to the report and leave them on classic art.

- [ ] **Step 3: Run checks**

Run: `./utility.sh --check-missing-sprites && make TREAT_WARNINGS_AS_ERRORS=true test`
Expected: no missing tileset sprites; tests pass; parity script OK.

- [ ] **Step 4: Commit**

```bash
git add mods/ra/tilesets/temperat.yaml mods/ra/mod.yaml OpenRA.Mods.Mobius
git commit -m "Add HD Temperate tileset for Red Alert"
```

### Task 6: HD Medium Tank

**Files:**
- Create: `mods/ra/sequences/vehicles-overrides.yaml`
- Modify: `mods/ra/mod.yaml` (`Sequences`: put `rahd|sequences/vehicles-overrides.yaml` immediately after `ra|sequences/vehicles.yaml`)
- Modify: `docs/remaster-ra-inventory.md` (2tnk frame layout, if refined)

**Interfaces:**
- Consumes: Task 1 (2tnk archive, frame ranges, muzzle archive), the `RemasteredFilename`/`RemasteredStart`/`RemasteredLength`/`RemasteredOffset`/`RemasteredScale` fields in `OpenRA.Mods.Mobius/RemasterSpriteSequence.cs`.
- Produces: HD sequences for `2tnk` (`idle`, `turret`, `muzzle`; `icon` stays classic, set `RemasteredFilename:` empty as TD HD does) and `2tnk.destroyed` (`idle`, `turret`).

- [ ] **Step 1: Write the overrides**, following the `mtnk`/`mtnk.destroyed` entries in `mods/cnc/sequences/vehicles-overrides.yaml`.

- [ ] **Step 2: Run checks**

Run: `./utility.sh --check-missing-sprites && make TREAT_WARNINGS_AS_ERRORS=true test`
Expected: clean; parity OK.

- [ ] **Step 3: Confirm resolution**

Run: `./utility.sh --resolved-sequences 2tnk` (if the engine names it differently, use its name).
Expected: `idle`, `turret`, `muzzle` and the husk sequences show `RemasteredFilename` paths that exist in the inventory.

- [ ] **Step 4: Commit**

```bash
git add mods/ra/sequences/vehicles-overrides.yaml mods/ra/mod.yaml docs/remaster-ra-inventory.md
git commit -m "Draw the Allied Medium Tank with Remastered HD art"
```

### Task 7: Rename to Red Alert HD, README, play-test checklist

**Files:**
- Modify: `mod.config` (`PACKAGING_INSTALLER_NAME="RedAlertHD"`, `PACKAGING_DISPLAY_NAME="Red Alert HD"`, `PACKAGING_WINDOWS_LAUNCHER_NAME="RedAlertHD"`, `PACKAGING_WINDOWS_INSTALL_DIR_NAME="Red Alert HD"`, `PACKAGING_WINDOWS_REGISTRY_KEY="OpenRARedAlertHD"`, `PACKAGING_COPY_ENGINE_FILES="./mods/common-content ./mods/ra"`; remove `PACKAGING_DISCORD_APPID` or leave it blank)
- Modify: `README.md` (what this is, that it is a fork of TiberianDawnHD, the macOS no-Steam install recipe from the Global Constraints, milestone-1 limits)
- Create: `docs/playtest-milestone1.md`

- [ ] **Step 1: Make the edits**

`docs/playtest-milestone1.md` holds the spec's user play-test checklist verbatim, plus the stock-client setup: the OpenRA `playtest-20261011` download and LAN host/join steps.

Version handshake: a source build reports `{DEV_VERSION}`, which a stock client rejects. Read how the engine's lobby compares mod versions, and document the exact command that makes a source build report `playtest-20261011` (expected: `make version VERSION=playtest-20261011`, which rewrites `Version:` in the mod.yaml files; do not commit its output). Run that command in a scratch copy, confirm `mods/ra/mod.yaml` shows `Version: playtest-20261011`, and record both in the playtest doc.

- [ ] **Step 2: Final verification**

Run: `make check && make check-packaging-scripts && make check-scripts && make TREAT_WARNINGS_AS_ERRORS=true test && ./utility.sh --check-missing-sprites && python3 tools/check_rules_parity.py`
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add mod.config README.md docs/playtest-milestone1.md
git commit -m "Name the mod Red Alert HD and add the milestone 1 play-test checklist"
```
