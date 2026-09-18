# Capability-Aware research website

Live hub: https://capability-aware.github.io/

The homepage presents a long-term physical intelligence agenda: understanding physical task boundaries, composing capabilities, acting autonomously, and advancing achievable performance. Locomotion and navigation are the current starting point. FDM, MPPI, RL, WAMs, and VLA models are methods within the agenda, not the definition of the initiative. The copy distinguishes research ambitions from current work.

The expandable website demo section preserves Nerfies and HyperNeRF as examples by their original authors, **not Capability-Aware publications**. All demo pages retain their attribution.

## Brand

Current GitHub avatar: `assets/brand/capability-aware-frontier.png` (light geometric mark on an opaque dark background). The earlier blue C-and-arrow files are retained as previous versions. Design rationale and the new generation prompt are in `assets/brand/FRONTIER.md`.

## Pages

| Page | URL | Source |
|---|---|---|
| Research hub | https://capability-aware.github.io/ | `index.html` |
| Nerfies demo | https://capability-aware.github.io/demo-nerfies/ | `demo-nerfies/index.html` |
| HyperNeRF demo | https://capability-aware.github.io/demo-hypernerf/ | `demo-hypernerf/index.html` |

Navigation includes the project menu, thumbnail/title links, paper/code/video links, a return-to-hub link, and a next-project link. Project pages include an MP4 player, original presentation embed, figures, and a copyable BibTeX citation. Core content and navigation work without JavaScript; only the copy button uses JavaScript.

## Edit and publish

Edit `projects.json`, then run:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
git add index.html projects.json assets demo-nerfies demo-hypernerf scripts README.md CREDITS.md .gitignore .nojekyll
git commit -m "Update research projects"
git push origin main
```

Shared styling: `assets/site.css`. Page structure: `scripts/build_site.py`. GitHub Pages publishes `main` / repository root; no Actions workflow or dependency installation is required. Generated HTML is committed, so GitHub does not run Python.

Local preview: `python3 -m http.server 8000`, then visit http://localhost:8000/.

## Separate project repositories

The currently published demos are **subdirectories in this repository**, not separate GitHub repositories. The existing token could upload files but the API rejected repository creation with HTTP 403. No independent demo repositories were created.

The same public paths can also be served by separate repositories named `demo-nerfies` and `demo-hypernerf` under the `Capability-Aware` account, each with its own GitHub Pages configuration. A project repository does not need `.github.io` in its name.

To prepare a self-contained project repository:

```sh
python3 scripts/export_project.py demo-nerfies
python3 scripts/export_project.py demo-hypernerf
```

Each `_export/<project>/` includes a standalone `index.html`, local assets, citation, and media credits. Navigation uses absolute URLs back to the hub and sibling project; styles and local media live inside that export. After creating the matching GitHub repository, push the exported folder and enable Pages from `main` / root. The exports are ignored by the main repository.

When an independent Pages site is working, remove the corresponding generated subdirectory from the hub repository and adjust the generator to stop generating it, avoiding two sources for the same public path. Keep the hub's link unchanged.

## Media

See [CREDITS.md](CREDITS.md). Nerfies' CC BY-SA assets are hosted here; HyperNeRF assets and the original YouTube presentations load from their respective providers. External playback depends on visitor network access. The MP4 players and direct-video links provide an alternative to YouTube embeds.

The old empty template remains at `templates/research-home.html` as a reference. The production site uses `projects.json` and the generator above.
