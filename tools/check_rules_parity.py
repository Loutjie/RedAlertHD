#!/usr/bin/env python3
"""Multiplayer guard: this mod's resolved rules/weapons must equal stock OpenRA RA.

For every actor and weapon defined by stock RA (engine/mods/ra), compares the engine
utility's resolved MiniYAML for stock RA against this mod's. Trait or field keys listed in
mods/ra/render-only-overrides.txt are removed from both sides first. Also compares the
Rules, Weapons and Missions lists of the two mod.yaml files (this mod may only append
rahd|rules/overrides.yaml to Rules). Exits 1 on any difference.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "engine")
STOCK_MOD = os.path.join(ENGINE, "mods", "ra")
OUR_MOD = os.path.join(ROOT, "mods", "ra")
ALLOW_LIST = os.path.join(OUR_MOD, "render-only-overrides.txt")
EXTRA_RULES = "rahd|rules/overrides.yaml"
LIST_KEYS = ("Rules", "Weapons", "Missions")


def top_level_names(path):
    names = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^([^\s#^][^:#]*):", line)
            if m:
                names.append(m.group(1).strip())
    return names


def mod_yaml_list(path, key):
    items, inside = [], False
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if re.match(r"^[^\s#]", line):
                inside = line.startswith(key + ":")
                continue
            if inside:
                item = line.split("#")[0].strip()  # a column-0 comment must not end the list
                if item:
                    items.append(item)
    return items


def referenced_files(mod_yaml, key):
    """Files named by a mod.yaml list: `ra|` is stock RA, `rahd|` is this mod."""
    dirs = {"ra": STOCK_MOD, "rahd": OUR_MOD}
    files = []
    for item in mod_yaml_list(mod_yaml, key):
        pkg, _, rel = item.partition("|")
        if pkg in dirs:
            files.append(os.path.join(dirs[pkg], rel))
    return files


def defined_names(mod_yaml):
    names = set()
    for key, kind in (("Rules", "rule"), ("Weapons", "weapon")):
        for f in referenced_files(mod_yaml, key):
            names |= {(kind, n) for n in top_level_names(f) if not n.startswith("^")}
    return names


def load_allow_list():
    allowed = []  # (scope, key, field)
    with open(ALLOW_LIST, encoding="utf-8") as f:
        for line in f:
            entry = line.split("#")[0].strip()
            if not entry:
                continue
            scope, _, target = entry.partition(":")
            trait, _, field = target.partition(".")
            allowed.append((scope.strip(), trait.strip(), field.strip()))
    return allowed


def parse(text):
    """Parse tab-indented MiniYAML into [(key, value, children)]."""
    root = []
    stack = [(-1, root)]
    for line in text.splitlines():
        if not line.strip():
            continue
        depth = len(line) - len(line.lstrip("\t"))
        content = line.strip()
        key, sep, value = content.partition(":")
        node = (key.strip(), value.strip(), [])
        while stack[-1][0] >= depth:
            stack.pop()
        stack[-1][1].append(node)
        stack.append((depth, node[2]))
    return root


def strip_allowed(tree, name, allowed):
    out = []
    for key, value, children in tree:
        removed = False
        for scope, trait, field in allowed:
            if scope not in (name, "^*") and not scope.startswith("^"):
                continue
            if key != trait:
                continue
            if not field:
                removed = True
                break
            children = [c for c in children if c[0] != field]
        if not removed:
            out.append((key, value, children))
    return out


def flatten(tree, prefix=""):
    lines = []
    for key, value, children in tree:
        path = prefix + key
        lines.append((path, value))
        lines.extend(flatten(children, path + "."))
    return lines


def utility_command(cwd, args, mod_arg):
    """Command line for the engine utility wrapper: utility.sh, or utility.cmd on Windows.

    Both wrappers take the mod id first (engine/) or read it from mod.config (repo root).
    """
    launcher = ["cmd", "/c", "utility.cmd"] if os.name == "nt" else ["./utility.sh"]
    return launcher + ([mod_arg] if mod_arg else []) + args


def run_utility(cwd, args, mod_arg):
    cmd = utility_command(cwd, args, mod_arg)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        return None, (p.stdout + p.stderr).strip()
    return p.stdout, None


def compare(kind, name, s, o):
    """Diff two flattened (path, value) lists; order is significant (trait order is tick order)."""
    found = []
    sd, od = dict(s), dict(o)
    for path in sorted(set(sd) | set(od)):
        if sd.get(path) != od.get(path):
            found.append(f"{kind} {name}: {path}: stock={sd.get(path)!r} ours={od.get(path)!r}")
    if s != o and not found:
        found.append(f"{kind} {name}: same keys and values but different order or duplicate keys")
    return found


def resolve(kind, name):
    flag = "--resolved-rules" if kind == "rule" else "--resolved-weapons"
    stock, err_s = run_utility(ENGINE, [flag, name], "ra")
    ours, err_o = run_utility(ROOT, [flag, name], None)
    return kind, name, stock, err_s, ours, err_o


def main():
    failures = []
    allowed = load_allow_list()

    # mod.yaml list comparison
    stock_yaml, our_yaml = os.path.join(STOCK_MOD, "mod.yaml"), os.path.join(OUR_MOD, "mod.yaml")
    for key in LIST_KEYS:
        s, o = mod_yaml_list(stock_yaml, key), mod_yaml_list(our_yaml, key)
        if key == "Rules":
            if not o or o[-1] != EXTRA_RULES:
                failures.append(f"mod.yaml {key}: last entry must be {EXTRA_RULES}")
            else:
                o = o[:-1]
        if s != o:
            failures.append(f"mod.yaml {key}: lists differ: stock-only={[x for x in s if x not in o]} "
                            f"ours-only={[x for x in o if x not in s]}")

    # Names defined by stock RA
    stock_names = defined_names(stock_yaml)
    jobs = sorted(stock_names)
    for kind, name in sorted(defined_names(our_yaml) - stock_names):
        failures.append(f"{kind} {name}: defined by this mod but not by stock RA")

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        results = list(pool.map(lambda j: resolve(*j), jobs))

    for kind, name, stock, err_s, ours, err_o in results:
        if stock is None or ours is None:
            failures.append(f"{kind} {name}: utility failed (stock: {err_s}; ours: {err_o})")
            continue
        s = flatten(strip_allowed(parse(stock), name, allowed))
        o = flatten(strip_allowed(parse(ours), name, allowed))
        if s == o:
            continue
        failures += compare(kind, name, s, o)

    if failures:
        print("parity FAILED")
        for f in failures:
            print("  " + f)
        return 1
    print(f"parity OK ({len(jobs)} actors/weapons compared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
