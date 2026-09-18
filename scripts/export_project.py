"""Export one generated page so it can be pushed to a separate Pages repo."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
projects = json.loads((ROOT/'projects.json').read_text())
slug = sys.argv[1] if len(sys.argv) == 2 else ''
project = next((p for p in projects if p['slug'] == slug), None)
if project is None:
    raise SystemExit('Choose a project: ' + ', '.join(p['slug'] for p in projects))
out = ROOT/'_export'/slug
out.mkdir(parents=True, exist_ok=True)
html = (ROOT/slug/'index.html').read_text()
html = html.replace('../assets/', './assets/').replace('../CREDITS.md', './CREDITS.md')
html = html.replace('href="../', 'href="https://capability-aware.github.io/')
(out/'index.html').write_text(html)
(out/'.nojekyll').touch()
shutil.copyfile(ROOT/'CREDITS.md', out/'CREDITS.md')
shutil.copyfile(ROOT/slug/'citation.bib', out/'citation.bib')
(out/'assets').mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets'/'brand', out/'assets'/'brand', dirs_exist_ok=True)
for name in ['site.css','site.js']:
    shutil.copyfile(ROOT/'assets'/name,out/'assets'/name)
for asset in [project['image'], project['video']] + [f['src'] for f in project['figures']]:
    if asset.startswith('assets/'):
        shutil.copyfile(ROOT/asset,out/asset)
(out/'README.md').write_text(f'# {project["name"]} — website framework demo\n\nOriginal research: {project["original"]}\n\nDemo page: https://capability-aware.github.io/{slug}/\n\nPublish main / root with GitHub Pages. See CREDITS.md for media attribution.\n')
print(out)
