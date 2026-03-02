# Release Notes - v1.1.0

## Highlights

- Fixed exact stat matching so `Speed` only matches `Speed`.
- Improved setup UI on small screens with a sticky `START AUTOMATION` button.
- Added vertical scrolling in setup when content exceeds window height.

## Fixes

- Prevented false positives where `AttackSpeed` or `CastingSpeed` could be counted as `Speed`.
- Improved OCR stat parsing by normalizing full detected labels before comparison.

## Documentation

- Added tool screenshot to [README.md](README.md).
- Added MIT [LICENSE](LICENSE) and linked it in README.

## Version

- Application version updated to `v1.1.0`.
- Window titles show setup/active mode with the current version.

---

Full changelog: https://github.com/ravenda900/flyff-autobod/commits/v1.1.0
