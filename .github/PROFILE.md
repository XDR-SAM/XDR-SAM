# Maintaining the living profile

## Automated updates

`.github/workflows/profile.yml` runs every six hours at minute 17, on relevant script/workflow pushes, and manually through Actions. Scheduled runs begin once the workflow is on the default branch. GitHub may delay scheduled jobs. The PR branch is included in the push trigger so the first refresh can be verified before merging.

The workflow uses its built-in `GITHUB_TOKEN` with `contents: write`; no personal token or added secret is required. Repository settings or branch protection that prohibit bot writes must be adjusted by the owner if encountered. It commits only `README.md` and `assets/live`. A failed data fetch exits before rendering so the last successful committed snapshot stays visible.

`python scripts/update_profile.py` fetches:

- Public owned repositories, with pagination. Latest projects exclude forks, archives, and this profile, and sort by push date. Bot pushes may affect ordering.
- Language bytes for the 30 most recently pushed public original active repositories. Percentages use all sampled language bytes, including languages below the six displayed. They measure neither skill nor coding time.
- GitHub's rolling-year contribution calendar and commit-contribution count through GraphQL. Counts reflect token visibility and GitHub contribution rules.
- Current and longest streaks from consecutive UTC calendar dates. Today may be incomplete; longest streak is bounded by the displayed year, not all time.

Local runs without a token use GitHub's public contribution calendar; the commit count reads `Pending` until an authenticated workflow run. Run `python scripts/update_profile.py --snapshot assets/live/snapshot.json` to render without fetching. The snake is an original SVG animation that sweeps the real calendar and fades visited contribution cells. No external snake service is required.

Run `python -m unittest discover -s scripts -p 'test_*.py'` to check streak boundaries, calendar parsing, and escaping of repository metadata. Do not place manual edits between `LATEST-PROJECTS` markers; the generator owns that block. The curated showcase outside the markers is maintained by hand.

## Design assets

The personal hero was generated using the built-in image-generation tool with both user-provided photographs as identity references. Its prompt is in `assets/banner-prompt.txt`. `sami-banner.webp` is a compressed encoding of the generated image, preserving its dimensions. It is static; the focus strip, contribution snake, language bars, and process line supply motion.

Technology chips are self-contained SVGs. Brand paths were sourced from Simple Icons; monograms are used where a path was unavailable. Names identify tools and model ecosystems, not partnerships or endorsements.

`python scripts/build_assets.py` regenerates the original alternate orbital heroes and process illustrations. Live SVG generation belongs to `update_profile.py`. All custom CSS animations have reduced-motion alternatives. Meaningful content has text labels or image alternative text. Expandable sections use GitHub-native `details`/`summary`; GitHub READMEs do not execute JavaScript.

Check desktop light/dark themes, a narrow viewport, image loading, expanded sections, and animation before publishing changes. Keep only the canonical `README.md`; do not recreate the case-conflicting `ReadMe.md`.
