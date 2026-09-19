# Capability Aware

Live website: https://capability-aware.github.io/

A minimal academic showcase: Research Projects dropdown, centered title and author, dark link buttons, teaser video, project previews, a short abstract, and project links.

## Update content

- `papers.json`: the Paper 1/2/3 placeholder names and paths. These have working standalone pages at `/paper1/`, `/paper2/`, and `/paper3/`.
- `scripts/build_site.py`: homepage text, link buttons, teaser, and project page content.
- `assets/site.css` and `assets/site.js`: shared layout and dropdown/carousel behavior.
- `projects.json`: archived Nerfies and HyperNeRF demonstration content. These are not Capability Aware publications.

The homepage uses seven user-provided BasicLoco videos in `assets/videos/`, configured in `videos.json`. Clicking a thumbnail switches the main player; without JavaScript each thumbnail opens the MP4 directly. Real World and Simulation buttons also open local videos. Original source videos are unchanged. Paper 1/2/3 remain placeholders in the research menu and list.

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Commit the generated HTML together with source changes. GitHub Pages publishes `main` / repository root. No build dependencies are required.

## Project pages

Project pages currently live in subdirectories of this repository. They are not separate GitHub repositories. Replace placeholders with research content when ready.

The archived demos remain at `/demo-nerfies/` and `/demo-hypernerf/`. They can still be exported with `python3 scripts/export_project.py demo-nerfies` (or `demo-hypernerf`). Exports are written to the ignored `_export/` folder.

See [CREDITS.md](CREDITS.md) for demo media attribution. The simplified layout follows the academic showcase structure of [Project Instinct](https://project-instinct.github.io/), with original site code and placeholder content.
