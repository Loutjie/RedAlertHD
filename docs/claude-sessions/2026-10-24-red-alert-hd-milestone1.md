# 2026-10-24 — Red Alert HD milestone 1 implementation

**Goal:** Execute the milestone 1 plan (`docs/superpowers/plans/2026-10-23-red-alert-hd-milestone1.md`):
a `ra` mod that runs stock OpenRA Red Alert from the Remastered install, with HD Temperate terrain
and an HD Medium Tank, everything else upscaled classic, multiplayer-compatible with stock RA.

## Key decisions

- **All four stock tilesets stay listed** (plan said Temperate only). Temperate-only broke
  `--check-yaml` on 70 stock maps and would make stock-hosted Snow/Interior/Desert maps
  unjoinable. Non-Temperate templates render upscaled classic art through a generic
  `Filename ??= Images` fallback in `RemasterTerrain.cs`. Rejected: Temperate-only + "unavailable".
- **Headless content mounting** via `HOME=<scratch>` with a scratch `settings.yaml` selecting the
  content source and a scratch Steam manifest (documented in `docs/remaster-ra-inventory.md`).
  Rejected: editing the user's real support dir or Steam files.
- **Audio manifests made data-driven** in `RemasterFileSystemLoader.cs` (TD defaults unchanged; RA
  sets empty lists so classic RA audio loads). Rejected: an RA-only copy of the loader.
- **Rules parity is strict**: order-sensitive, and fails on any actor/weapon our mod adds.
  Separate `tools/check_tileset_parity.py` guards template Id/Size/terrain types.
- **Aftermath `sounds.mix` mounted before base** so the base game's two differing `.aud` files win,
  matching stock.
- **2tnk frame layout** verified against the game's own `RA_UNITS.XML` (body 0–31, turret 32–63);
  no per-facing offsets needed. Muzzle plays all 10 HD frames (render-only).
- **`luac` not installed** (system-wide); `make check-scripts` not run — no Lua changed.

## Commits (feature/milestone-1, from design/milestone-1 @ 21a76ce)

- Inventory: ba7e870, f9f20d1
- Scaffold + classic tileset fallback: f71bd12, b1d100a
- Rules parity: 36823fe, 0b990f5
- Content loading + data-driven audio: de8c646, 4f936f3
- HD Temperate tileset: 0774700
- HD Medium Tank: 01d351a
- Rename, README, play-test doc: 0ad86ef
- Final-review fixes: 4314528

## Deferred items

- Windows `make.ps1 test` rules-parity step: `utility.cmd` drops the mod id on the root call and
  its `EXIT /B 0` hides failures. Fix by calling `bin\OpenRA.Utility.exe` directly or skipping on Windows.
- Parity tooling gaps: sequences/`Remastered*Length` not guarded (milestone 2 risk), allow-list `^`
  scope is global, malformed/stale allow-list lines unreported.
- `make test` no longer lint-checks `cnc`/`remaster-content`.
- `DiscordService.ApplicationId` still stock RA's; `AudioStyle: remastered` option is inert.
- Packaging drops `./mods/cnc` from `PACKAGING_COPY_ENGINE_FILES`.

## Open questions

- Not yet seen running: HD terrain/tank appearance, muzzle placement, classic-tile sheet usage,
  LAN join with stock `playtest-20261011` (user play-test, `docs/playtest-milestone1.md`).
- User must add `"StateFlags" "4"` to `appmanifest_1213210.acf` before the in-game selector finds the install.
