# rust-deck-plugins

The plugin list of [rust-deck](https://github.com/NicolaiVdS/rust-deck): **Plugins** in its GUI
reads `index.json` from here. Every plugin in it was reviewed by the maintainer before it was
merged.

## Layout

- `index.json`: the list. Its format is in rust-deck's README,
  [Publishing a plugin](https://github.com/NicolaiVdS/rust-deck#publishing-a-plugin).
- `plugins/<id>/`: a plugin's source, what the reviewer reads (and a fine `homepage`).
- `zips/<id>-<version>.zip`: what rust-deck downloads, built from `plugins/<id>/`.

## Adding or updating a plugin

Writing one: [rust-deck's README](https://github.com/NicolaiVdS/rust-deck#writing-a-plugin) has the
manifest and the protocol. Then open a pull request with:

1. `plugins/<id>/`: the plugin's files.
2. `zips/<id>-<version>.zip`, from rust-deck's
   `registry/zip-plugin.sh plugins/<id> zips/<id>-<version>.zip`, on Linux or macOS. It prints the
   zip's sha256 and size.
3. The plugin's entry in `index.json`, with that sha256 and size and
   `"url": "https://raw.githubusercontent.com/NicolaiVdS/rust-deck-plugins/main/zips/<id>-<version>.zip"`.

Every version is a new zip next to the older ones, and the entry moves to it. Never replace or
change a published zip: installs check it against the entry's sha256, and it's what was reviewed.

CI checks the list: its format, and that each zip in `zips/` has its entry's sha256 and size. Run the
same check yourself with `python3 .github/check-index.py`.

## Reviewing

- Rebuild the zip from `plugins/<id>/` with `registry/zip-plugin.sh` and compare its sha256 and size
  with the entry: then the zip holds exactly the source you read.
- Read all the code, and what it downloads or runs: plugins run with their users' rights, so they
  can do whatever their users can.
- No published zip was changed or removed, and the entry's `platforms`, `needs` and `homepage` are
  right.
