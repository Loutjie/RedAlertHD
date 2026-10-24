#!/usr/bin/env python3
"""Multiplayer guard: this mod's HD tilesets must equal stock OpenRA RA in everything but art.

For every rahd|tilesets/<name>.yaml in mods/ra/mod.yaml, compares it with stock
engine/mods/ra/tilesets/<name>.yaml: the General section (except the sheet-size field,
which RemasterTerrain names IndexedSheetSize), the whole Terrain section, every template's
fields except art (Images/Filename/RemasteredFilenames) in the same order, the template
Images == Filename names, and MultiBrushCollections. Terrain types decide pathing, so any
difference desyncs against stock. Also checks the TileSets list names the same files in
the same order as stock. Pass -v to list templates without Remastered art. Exits 1 on any
difference.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_MOD = os.path.join(ROOT, "engine", "mods", "ra")
OUR_MOD = os.path.join(ROOT, "mods", "ra")
ART_KEYS = {"Images", "Filename", "RemasteredFilenames", "RemasteredCompositeFilenames"}
SHEET_KEYS = {"SheetSize", "IndexedSheetSize"}


def parse(path):
    """Minimal MiniYAML reader: a list of (key, value, children) by tab depth."""
    root = []
    stack = [(-1, root)]
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            depth = len(line) - len(line.lstrip("\t"))
            key, _, value = line.strip().partition(":")
            node = (key, value.strip(), [])
            while stack[-1][0] >= depth:
                stack.pop()
            stack[-1][1].append(node)
            stack.append((depth, node[2]))
    return root


def as_dict(nodes):
    return {k: (v, as_dict(c)) for k, v, c in nodes}


def section(doc, name):
    return next((c for k, _, c in doc if k == name), [])


def tileset_list(path):
    items, inside = [], False
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if re.match(r"^\S", line):
                inside = line.startswith("TileSets:")
            elif inside and line.strip():
                items.append(line.strip())
    return items


def compare(stock_path, ours_path, verbose):
    errors = []
    stock, ours = parse(stock_path), parse(ours_path)
    if [n[0] for n in stock] != [n[0] for n in ours]:
        errors.append("top-level sections differ")

    general = [{k: v for k, v, _ in section(d, "General") if k not in SHEET_KEYS} for d in (stock, ours)]
    if general[0] != general[1]:
        errors.append("General differs")

    for name in ("Terrain", "MultiBrushCollections"):
        if as_dict(section(stock, name)) != as_dict(section(ours, name)):
            errors.append(f"{name} differs")

    stock_templates, our_templates = section(stock, "Templates"), section(ours, "Templates")
    if [t[0] for t in stock_templates] != [t[0] for t in our_templates]:
        errors.append("template keys or order differ")

    classic_only = []
    for (key, _, s), (_, _, o) in zip(stock_templates, our_templates):
        s, o = as_dict(s), as_dict(o)
        if {k: v for k, v in s.items() if k not in ART_KEYS} != {k: v for k, v in o.items() if k not in ART_KEYS}:
            errors.append(f"{key}: Id/Size/Tiles/Categories differ")
        filename = o.get("Filename", o.get("Images", ("", {})))[0]
        if s["Images"][0] != filename:
            errors.append(f"{key}: Images {s['Images'][0]} != {filename}")
        if "RemasteredFilenames" not in o and "RemasteredCompositeFilenames" not in o:
            classic_only.append(f"{s['Id'][0]} {filename}")

    name = os.path.relpath(ours_path, ROOT)
    print(f"  {name}: {len(stock_templates)} templates, {len(classic_only)} without Remastered art")
    if verbose:
        for t in classic_only:
            print(f"    classic only: {t}")
    return [f"{name}: {e}" for e in errors]


def main():
    verbose = "-v" in sys.argv[1:]
    errors = []
    stock_list = tileset_list(os.path.join(STOCK_MOD, "mod.yaml"))
    our_list = tileset_list(os.path.join(OUR_MOD, "mod.yaml"))
    if [i.split("|", 1)[1] for i in stock_list] != [i.split("|", 1)[1] for i in our_list]:
        errors.append(f"TileSets list differs: {our_list} vs stock {stock_list}")

    for item in our_list:
        package, path = item.split("|", 1)
        if package == "rahd":
            errors += compare(os.path.join(STOCK_MOD, path), os.path.join(OUR_MOD, path), verbose)

    if errors:
        print("tileset parity FAILED")
        for e in errors:
            print("  " + e)
        return 1

    print("tileset parity OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
