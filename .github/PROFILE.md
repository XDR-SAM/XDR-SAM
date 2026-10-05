# Maintaining the profile

`README.md` is the canonical profile. Project links and descriptions are curated in Markdown; update them when the work changes. Research descriptions should distinguish completed experiments from planned work.

## Artwork

Run `python scripts/build_assets.py` from the repository root using Python 3. The generator uses only the standard library and writes eight SVG files to `assets/`: desktop and mobile hero/process illustrations in light and dark palettes.

The graphics contain their own styles, no JavaScript, no external fonts, and no remote image dependencies. Motion is decorative; all text is visible on the first frame. CSS animations respect `prefers-reduced-motion` in supporting viewers. The README uses `<picture>` to select viewport and color-scheme variants, with a light desktop fallback.

The mobile artwork breakpoint is 600 CSS pixels. Check the README in both GitHub themes and at a narrow viewport when making layout changes. Essential information, project links, and contact links also exist as real README text.

The old banners, duplicate `ReadMe.md`, and unused snake/project-panel generators have been retired. The profile no longer depends on scheduled asset generation or external stats-card services.
