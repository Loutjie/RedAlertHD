# Red Alert HD — Milestone 1 design: the HD pipeline, proven on one unit

Date: 2026-10-23
Repo: Loutjie/RedAlertHD (fork of OpenRA/TiberianDawnHD), local clone `~/Projects/RedAlertHD`

## Intent

The user wants to play OpenRA Red Alert skirmishes against the AI with the crisp HD art from
the C&C Remastered Collection (which they own), while staying able to play LAN/online against
people running stock OpenRA Red Alert. The campaign comes later; stock OpenRA RA already ships
~45 missions, so the campaign is an art job, not a mission-porting job.

Milestone 1 exists to prove the whole pipeline end to end before anyone maps hundreds of
sequences: Red Alert loads from the user's Remastered install, the map draws in HD, one unit
draws in HD, everything else still shows (upscaled classic art), and the build still joins a
stock OpenRA RA game.

## Goals (milestone 1)

1. A Red Alert mod (`mods/ra` in this repo) that boots with assets read from the user's
   Remastered Collection install (Steam origin), with no assets copied into the repo.
2. The **Temperate** tileset rendered from Remastered HD terrain.
3. **One unit in HD: the Allied Medium Tank (`2tnk`)** — body, turret, muzzle flash, husk.
   Chosen because it exercises a turreted vehicle, facings, a muzzle effect and a husk in one
   actor. *(Builder's call, made in brainstorming; change freely.)*
4. Every other unit, building, effect and UI piece still renders, using the classic RA sprite
   upscaled by the existing fallback in `RemasterSpriteSequence` (it upscales classic art by
   `RemasteredTileSize / TileSize` when no `RemasteredFilename` is given). Nothing may be invisible.
5. **Multiplayer compatibility:** a game hosted by this build can be joined by stock OpenRA RA
   of the same engine version, and vice versa, on a stock RA skirmish map.
6. CI (`make check`, `make test`) passes.

## Non-goals (milestone 1)

- Mapping any unit, building, infantry or effect other than `2tnk`.
- Snow, Interior and Desert tilesets.
- HD sidebar/UI, cameos, cursors, fonts.
- Remastered audio and music (classic audio is fine).
- Campaign missions, FMV videos (Bink), map editor polish, packaging/installers, macOS DMG.
- Performance work (TD HD itself is flagged unoptimised).
- Any upstream PR or community post.

## Anti-goals (would be failure even if it "works")

- **Any change to gameplay rules, weapons, AI or maps** relative to stock OpenRA RA. Online
  compatibility depends on identical rules; only rendering/audio/content-loading may differ.
  The only allowed rules edits are render-only trait swaps of the kind TD HD makes in
  `mods/cnc/rules/overrides.yaml` (e.g. `-TerrainRenderer` → `RemasterTerrainRenderer`, cloak
  style), and each must be checked not to break sync.
- **Committing, copying or redistributing any original or Remastered game file** (MIX, MEG,
  TGA/DDS/ZIP art, XML tile mappings, audio). The mod only references paths inside the user's
  install. Derived output that embeds EA art (e.g. extracted frames) must not be committed either.
  Generated YAML that only names files and frame indices is fine (TD HD commits the same kind).
- Invisible actors, or a fallback that silently hides missing art.
- Forking the shared C# so far from upstream TiberianDawnHD that its fixes can no longer be merged.

## Constraints

- Engine: OpenRA `playtest-20261011` (the fork's pinned `ENGINE_VERSION`); stock RA for
  compatibility testing must be the same version.
- Mod identity must match stock RA for multiplayer: `Metadata`/mod ID `ra`, the same rules,
  weapons, maps and `SupportsMapsFrom: ra`. TD HD does exactly this for `cnc` (its `mod.config`
  has `MOD_ID="cnc"` and its mod.yaml pulls every rules file from the engine's `cnc|` package).
- Code style: the repo's `.editorconfig`; run the Makefile's `check`/`test`.
- Git: work on feature branches, one concern per branch; commit identity Loutjie Coetzee
  <lccoetzee@gmail.com> (repo-local); trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  No pushes or PRs without the user's go-ahead.
- Never launch the game from an agent; the user play-tests. Agents may run the OpenRA Utility
  (`./utility.sh`) headless for checks.
- macOS host. dotnet SDK 10.0.402 is installed. **The Remastered Collection is not installed on
  this Mac yet** (no Steam). See "Open questions".

## How it is built (decided)

- **Layout: add `mods/ra` next to the existing `mods/cnc`, mirroring its structure**
  (`mod.yaml`, `rules/overrides.yaml`, `sequences/*-overrides.yaml`, `tilesets/temperat.yaml`,
  `bits/`). Leave `mods/cnc` and the shared `OpenRA.Mods.Mobius` code untouched where possible
  so upstream TiberianDawnHD fixes keep merging. `mod.config` switches `MOD_ID` to `ra` and the
  packaging names to "Red Alert HD". *(Builder's call; the alternative — deleting `mods/cnc` — was
  rejected because it makes every upstream merge conflict and loses the working reference.)*
- **Mod.yaml pattern, copied from TD HD:** rules/weapons/maps come straight from the engine's
  `ra|` package unchanged; this mod overlays only sequences, tilesets, render-only rules overrides,
  chrome where needed, and sets `MapGrid.TileSize: 128,128`, `TerrainFormat: RemasterTerrain`,
  `SpriteSequenceFormat: RemasterSpriteSequence`, `FileSystem: RemasterFileSystem`.
- **Content:** a `ContentSources` entry for the Remastered Steam origin (AppId 1213210),
  mounting the RA classic MIX files that ship inside the Remastered install (under
  `Data/CNCDATA/RED_ALERT/...`, exact names to be read from the install) plus
  `TEXTURES_RA_SRGB.MEG`, `TEXTURES_COMMON_SRGB.MEG` and the config MEG holding the tileset XMLs.
  A `remaster-content`-style selector mod for RA, mirroring `mods/remaster-content`.
- **Terrain:** generate `mods/ra/tilesets/temperat.yaml` from the engine's RA temperate tileset with
  the existing `RemasterTilesetConverter` utility command (its Desc already says "Convert a TD or RA
  tileset to remaster format"), using the RA temperate XML from the Remastered config MEG.
- **The unit:** `mods/ra/sequences/vehicles-overrides.yaml` adds `RemasteredFilename` (and start/
  length/offset/scale fields as needed) for `2tnk`, its turret, muzzle and husk, following the
  `mtnk` entries in `mods/cnc/sequences/vehicles-overrides.yaml`.

## Verification (definition of done)

Checks an agent can run:
- `make` and `make check` / `make test` pass; the OpenRA Utility's `--check-yaml` (or the
  Makefile's equivalent) reports no errors for `ra`.
- A headless check that every RA actor's sequences resolve (no missing-sprite errors), so the
  "nothing invisible" goal is tested, not assumed.
- A diff check that the resolved rules and weapons of this mod equal stock RA's apart from the
  allow-listed render-only overrides (the multiplayer anti-goal, made testable).

User play-test checklist (written into the PR description):
- The mod starts, finds the Remastered install, and loads a stock RA skirmish map on Temperate.
- Terrain is HD; a Medium Tank is HD in all 32 facings, turret rotates, fires with HD muzzle,
  leaves an HD husk.
- Other units/buildings visible (upscaled classic).
- Host a LAN game in this build; join from stock OpenRA RA `playtest-20261011`; play 5 minutes
  without a desync.

## Left to the builder

- Exact Remastered file names and frame layouts for RA (read them from the install's MEGs).
- Whether RA needs any C# changes in `OpenRA.Mods.Mobius` (e.g. RA-specific MIX names, palette or
  shadow handling, tileset XML naming); keep any such change minimal and RA-specific files separate.
- How the headless sequence/rules checks are implemented (utility command, script, or test).
- Milestone 2+ ordering (remaining units, buildings, other tilesets, UI, audio, campaign art).

## Calls made after the builder check (builder's calls unless marked)

- **Install first.** Everything past scaffolding needs the Remastered install, so the plan's first
  step is the install; tasks that need real files are ordered after it and none are "done" on
  guessed paths or frame layouts.
- **`mods/cnc` stays as a buildable reference**; `MOD_ID`, CI's `make check`/`make test` and
  packaging target `ra`. RA gets its own selector mod (`mods/ra-remaster-content`), copied from
  `mods/remaster-content`, rather than sharing it.
- **Version handshake:** copy TD HD's approach exactly (`Version: {DEV_VERSION}` plus
  `PACKAGING_OVERWRITE_MOD_VERSION`) and verify against the engine's lobby/version check before
  claiming the multiplayer goal.
- **Render-only allow-list is open but written down:** a committed allow-list file names each
  rules override with a one-line reason it cannot affect sync; the builder may add entries.
  `MapGrid.TileSize: 128,128` is taken as render-only on the precedent that TD HD ships it and
  stays multiplayer-compatible; the rules-diff check plus the LAN play-test confirm it for RA.
- **C# budget:** RA-specific code goes in new files; edits to existing shared Mobius files are
  allowed only when small and generic (useful to TD too), each noted in the PR description.
- **Tiles or sprites with no Remastered counterpart** (any Temperate template, ore/gem, bridge)
  fall back to upscaled classic art; the "nothing invisible" check passes when every sequence and
  template resolves to some sprite.

## Open questions (need the user)

1. **Installing the Remastered Collection on this Mac.** It requires installing Steam (system-wide
   software) and the macOS manifest workaround from the TD HD README, then a large download.
   Nothing past the scaffolding can be verified without it.
