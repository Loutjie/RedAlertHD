# Red Alert HD, milestone 1 play-test

Milestone 1 has not been seen running yet. Everything below is the checklist for the first run.

## Before you start

1. **Fix the Steam app manifest (required on this Mac).** The mod's content finder
   (`SteamContentOrigin`) accepts an install only if `appmanifest_1213210.acf` contains
   `"StateFlags" "4"`, an `installdir` key, and that `steamapps/common/<installdir>` exists.
   The manifest currently on this Mac is a stub without `StateFlags`, so the in-game content
   selector finds nothing. Replace the contents of
   `~/Library/Application Support/Steam/steamapps/appmanifest_1213210.acf` with:
   ```
   "AppState"
   {
   	"appid"		"1213210"
   	"Universe"		"1"
   	"installdir"		"CnCRemastered"
   	"StateFlags"		"4"
   }
   ```
   Note `4` (fully installed), not the `1026` that the Tiberian Dawn HD README uses. With `1026` Steam
   would try to download the game, but this mod's finder would reject the install. Steam itself
   is not installed here, so nothing else rewrites that file.
2. Build and start: `make`, then `./launch-game.sh`. In the content prompt pick the Remastered
   source (artwork: Remastered, audio: Classic).

## Known limits in milestone 1

- Only the Temperate tileset is HD. Snow, Interior and Desert maps load with upscaled classic
  terrain. This is the intended milestone-1 behaviour.
- Only `2tnk` (Allied Medium Tank) is HD. Every other unit and building is upscaled classic art.
- Trees, ore, gems, the ore mine and the building-placement overlay are HD on Temperate. On Snow,
  the `t15` and `tc01`..`tc05` husks stay classic (their Snow archives are incomplete).
- The `2tnk` muzzle flash plays all 10 HD frames, so it lasts about twice as long as stock. This is
  cosmetic and does not affect sync.
- Audio is classic.
- Not seen running yet.

## Checklist

- The mod starts, finds the Remastered install, and loads a stock RA skirmish map on Temperate.
- Terrain is HD; a Medium Tank is HD in all 32 facings, turret rotates, fires with HD muzzle,
  leaves an HD husk.
- Trees, ore, gems and the ore mine are HD and sit where the classic ones did (no shift against
  the terrain grid); destroying a tree plays its burn-down. Placing a building shows the HD
  green/red footprint.
- Other units/buildings visible (upscaled classic).
- Host a LAN game in this build; join from stock OpenRA RA `playtest-20261011`; play 5 minutes
  without a desync.

## Stock client setup for the LAN test

1. Download OpenRA `playtest-20261011` from <https://www.openra.net> (playtest builds are listed
   on the download page and in the OpenRA GitHub releases) and install it on the second machine.
   It needs its own Red Alert game content (the in-game content installer fetches it).
2. **Version handshake.** The server rejects a client whose mod id or mod version differs
   (`engine/OpenRA.Game/Server/Server.cs`, handshake: `Manifest.Id != handshake.Mod`, then
   `Manifest.Metadata.Version != handshake.Version`, and an orders-protocol check). The mod id is
   `ra` in both builds. A source build reports its `Metadata.Version`, which is `{DEV_VERSION}`
   here, and a stock `playtest-20261011` client reports `playtest-20261011`, so they refuse each
   other. To make the source build report the stock version, set the version in `mods/ra/mod.yaml`:

   ```sh
   make version VERSION=playtest-20261011
   ```

   This runs the engine's `set_mod_version` over `mods/$(MOD_ID)/mod.yaml` only, so just
   `mods/ra/mod.yaml` changes. `mods/ra-remaster-content` and `mods/cnc` keep `{DEV_VERSION}`.
   It rewrites the `Version:` line, so **never commit its output**; undo it with
   `git checkout mods/ra/mod.yaml`. Packaged builds do this automatically
   (`PACKAGING_OVERWRITE_MOD_VERSION="True"`).
   The engine itself is already `playtest-20261011` (`ENGINE_VERSION` in `mod.config`, `engine/VERSION`),
   built from the same source, so the orders protocol matches. Nothing else needs changing.
3. Verified 2026-10-24 in a scratch copy (mods, `Makefile` and `mod.config` rsynced, `engine`
   symlinked, copy deleted afterwards): after the command, `mods/ra/mod.yaml` line 3 read
   `Version: playtest-20261011`; the other three mods still read `Version: {DEV_VERSION}`.
4. Host in this build: Multiplayer, Create Server (LAN), pick a stock RA skirmish map with Temperate
   terrain. On the stock client: Multiplayer, Direct Connect (or the LAN list), enter the host's IP and
   port 1234. Play 5 minutes; a desync shows as a lobby/in-game "out of sync" message and a
   `syncreport.log` in the OpenRA support directory.

## Extra checks (not part of the spec checklist)

- Random/generated map: in the lobby, check that a random or generated map either is not offered or
  works between this build and stock Red Alert.

## Headless checks (no game launch)

```sh
make check && make check-packaging-scripts && make check-scripts && make TREAT_WARNINGS_AS_ERRORS=true test
python3 tools/check_rules_parity.py       # also run by make test, along with tools/check_tileset_parity.py
```

`./utility.sh --check-missing-sprites` fails with `blank.png not found` when run plainly, because
content is mounted only after a content source is chosen in the game. Use the scratch-`HOME` recipe in
`docs/remaster-ra-inventory.md` ("Headless checks"): a scratch `HOME` holding a `settings.yaml` with
`ContentSource@ra`, a manifest with `"StateFlags" "4"`, and a symlink to the real install.

`make check-scripts` needs `luac` (Lua) on the PATH.
