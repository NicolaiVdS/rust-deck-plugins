#!/usr/bin/env python3
# What CI checks in index.json: valid JSON with "version": 1, every entry one rust-deck can read (it
# skips the others, so they'd just be missing from the GUI), and every download in this repo's zips/
# there with its entry's sha256 and size. Standard library only. From the repository's top:
#   python3 .github/check-index.py
import hashlib, json, re, sys

ZIPS = "https://raw.githubusercontent.com/NicolaiVdS/rust-deck-plugins/main/zips/"
TEXT = ("id", "name", "description", "author", "homepage", "version")


def strings(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def reject(constant):  # Python reads NaN and Infinity; rust-deck would refuse the whole list
    raise ValueError(f"{constant} isn't JSON")


def problems(index):
    if not isinstance(index, dict) or type(index.get("version")) is not int or index["version"] != 1:
        yield 'needs "version": 1'
    plugins = index.get("plugins") if isinstance(index, dict) else None
    if not isinstance(plugins, list):
        yield 'needs a "plugins" list'
        return
    seen = set()
    for p in plugins:
        if not isinstance(p, dict):
            yield f"not an object: {p!r}"
            continue
        pid, d = p.get("id"), p.get("download")
        d = d if isinstance(d, dict) else {}
        bad = [k for k in TEXT if not isinstance(p.get(k), str)]
        bad += [k for k, v in (("platforms", p.get("platforms")), ("needs", p.get("needs", []))) if not strings(v)]
        bad += [f"download.{k}" for k in ("url", "sha256") if not isinstance(d.get(k), str)]
        if type(d.get("size")) is not int or d["size"] < 0:
            bad.append("download.size")
        if bad:
            yield f"{pid!r}: missing or the wrong type: {', '.join(bad)}"
            continue
        if not re.fullmatch(r"[a-z0-9_-]+", pid) or re.fullmatch(r"con|prn|aux|nul|com[0-9]|lpt[0-9]", pid):
            yield f"{pid!r}: an id matches ^[a-z0-9_-]+$ and isn't a Windows device name (con, com1…)"
            continue
        if pid in seen:
            yield f"{pid!r}: listed twice"
        seen.add(pid)
        if not d["url"].startswith(ZIPS):
            continue  # hosted elsewhere: the reviewer downloads and checks it
        name = f"{pid}-{p['version']}.zip"
        if d["url"] != ZIPS + name:
            yield f"{pid!r}: its download.url should be {ZIPS}{name}"
            continue
        try:
            with open(f"zips/{name}", "rb") as f:
                data = f.read()
        except OSError as e:
            yield f"{pid!r}: {e}"
            continue
        sha256 = hashlib.sha256(data).hexdigest()
        if (sha256, len(data)) != (d["sha256"], d["size"]):
            yield f"{pid!r}: zips/{name} has sha256 {sha256} and size {len(data)}, not {d['sha256']} and {d['size']}"


try:
    with open("index.json", encoding="utf-8") as f:
        index = json.load(f, parse_constant=reject)
except (OSError, ValueError) as e:
    sys.exit(f"index.json: {e}")
errors = [f"index.json: {e}" for e in problems(index)]
print("\n".join(errors) or f"index.json: ok ({len(index['plugins'])} listed)", file=sys.stderr if errors else sys.stdout)
sys.exit(1 if errors else 0)
