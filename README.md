# Capability Aware

Live website: https://capability-aware.github.io/

A minimal academic showcase: Research Projects dropdown, centered title and author, dark link buttons, teaser video, project previews, a short abstract, and project links.

## Update content

- `featured-video.json`: main homepage video (currently TempoLoco).
- `links.json`: homepage black buttons. Fill the empty YouTube/Bilibili `url` values to activate them.
- `papers.json`: research page titles, paths, status, and content. The first paper has a standalone page at `/beyond-fixed-visual-history/`; `/paper1/` redirects there. Paper 2/3 are still placeholders.
- `scripts/build_site.py`: homepage text, link buttons, teaser, and project page content.
- `assets/site.css` and `assets/site.js`: shared layout and dropdown/carousel behavior.
- `projects.json`: archived Nerfies and HyperNeRF demonstration content. These are not Capability Aware publications.

The homepage features TempoLoco in the main player. The horizontal strip contains six BasicLoco real-world videos from `videos.json`, playing muted on a loop with native playback controls. Simulation is excluded from the strip. The first research entry is **Beyond Fixed Visual History: Learning Motion-Adaptive Temporal Receptive Fields for Complex-Terrain Quadruped Locomotion**. Its standalone page presents the supplied manuscript and demonstration compilation; public paper links and citation metadata remain pending.

## First paper: preparing the release

The author order and affiliations, abstract, method summary, three figures, and selected experimental results are now taken from the manuscript supplied on October 10, 2026. The TempoLoco compilation is embedded beneath the overview figure. The manuscript reports simulation and hardware trial counts separately from the full-curriculum comparison; the arm is fixed and policy inference uses an external workstation. These are manuscript-reported results, not an acceptance announcement.

Edit the first entry in `papers.json` for future content updates. Paper/arXiv/code URLs and BibTeX remain empty until their public records are supplied; unavailable URLs render as labels rather than fake links. Update `status` when the arXiv record is available. Figures live in `assets/papers/tempoloco/`. The published TempoLoco video has `Hao Zhang | HaoZhangRobotics.github.io` burned into every frame; the poster is extracted from that version. Original video and manuscript source files are preserved outside published output. Do not commit the manuscript ZIP or extracted LaTeX project.

The standalone layout follows the centered title, author block, resource buttons, teaser, and section structure of [Embrace Collisions](https://project-instinct.github.io/embrace-collisions/), using original HTML/CSS and no copied research media or text.

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Commit the generated HTML together with source changes. GitHub Pages publishes `main` / repository root. No build dependencies are required.

## Project pages

Project pages currently live in subdirectories of this repository. They are not separate GitHub repositories. Replace placeholders with research content when ready.

The archived demos remain at `/demo-nerfies/` and `/demo-hypernerf/`. They can still be exported with `python3 scripts/export_project.py demo-nerfies` (or `demo-hypernerf`). Exports are written to the ignored `_export/` folder.

See [CREDITS.md](CREDITS.md) for demo media attribution. The simplified layout follows the academic showcase structure of [Project Instinct](https://project-instinct.github.io/), with original site code and placeholder content.
