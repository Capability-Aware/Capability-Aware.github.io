"""Generate a static research hub and self-contained project page content."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'projects.json').read_text())
e = escape

def asset(url, prefix):
    return url if url.startswith(('https://', 'http://')) else prefix + url

def button(label, href, secondary=False):
    return f'<a class="button{" secondary" if secondary else ""}" href="{e(href)}">{e(label)}</a>'

def shell(title, body, prefix='', description='Capability-Aware research project website demonstration.'):
    menu = ''.join(f'<a href="{prefix}{p["slug"]}/">{e(p["name"])} <small>· demo</small></a>' for p in PROJECTS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}">
<link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<div class="topbar"><nav class="container nav" aria-label="Main navigation">
<a class="brand" href="{prefix or './'}">Capability-Aware</a><div class="nav-right">
<a href="{prefix or './'}#research">Research</a>
<details><summary>Projects</summary><div class="menu">{menu}</div></details>
<a class="github-nav" href="https://github.com/Capability-Aware">GitHub ↗</a></div></nav></div>
{body}
<footer><div class="container"><p>Capability-Aware · Research website demo</p>
<p>Example research belongs to its original authors. <a href="{prefix}CREDITS.md">Media credits</a> · <a href="https://github.com/Capability-Aware/Capability-Aware.github.io">Website source</a></p></div></footer>
</body></html>'''

def build_home():
    cards = []
    for p in PROJECTS:
        links = button('Project page ↗', p['slug']+'/') + button('Paper', p['paper'], True) + button('Code', p['code'], True) + button('Video', 'https://www.youtube.com/watch?v='+p['youtube'], True)
        cards.append(f'''<article class="project">
<a class="thumbnail" href="{p['slug']}/"><img src="{e(p['image'])}" alt="{e(p['imageAlt'])}" width="660" height="430"><span class="image-label">Explore project ↗</span></a>
<div><span class="badge">DEMO PROJECT</span><h3><a href="{p['slug']}/">{e(p['title'])}</a></h3>
<p class="authors">{e(p['authors'])}</p><p class="venue">{e(p['venue'])}</p><p>{e(p['summary'])}</p><div class="buttons">{links}</div></div></article>''')
    body = f'''<header class="container hero"><div class="eyebrow">Research projects</div><h1>Capability-Aware</h1>
<p class="intro">A home for papers, project pages, and open-source research.</p>
<div class="buttons">{button('Explore projects', '#research')}{button('GitHub ↗', 'https://github.com/Capability-Aware', True)}</div></header>
<main id="main" class="container"><aside class="notice"><strong>Framework demo / 框架演示</strong> — Two published papers are used here to demonstrate navigation and media. They are not Capability-Aware publications.</aside>
<section id="research" aria-labelledby="research-title"><div class="heading"><h2 id="research-title">Research Projects</h2><span>2 demonstration pages</span></div>{''.join(cards)}</section></main>'''
    (ROOT/'index.html').write_text(shell('Capability-Aware | Research Projects', body))

def build_project(p):
    folder = ROOT / p['slug']
    folder.mkdir(exist_ok=True)
    prefix = '../'
    links = ''.join([button('Paper',p['paper']),button('Code',p['code']),button('Video','https://www.youtube.com/watch?v='+p['youtube']),button('Original project ↗',p['original'],True)])
    gallery = ''.join(f'<figure><img src="{e(asset(f["src"],prefix))}" alt="{e(f["alt"])}" loading="lazy"><figcaption>{e(f["caption"])}</figcaption></figure>' for f in p['figures'])
    other = next(x for x in PROJECTS if x['slug'] != p['slug'])
    video = asset(p['video'], prefix)
    body = f'''<header class="container hero"><span class="badge">DEMONSTRATION PROJECT · ORIGINAL AUTHORS CREDITED</span>
<h1 class="paper-title">{e(p['title'])}</h1><p class="authors">{e(p['authors'])}</p><p class="affiliations">{e(p['affiliations'])}</p>
<p class="venue">{e(p['venue'])}</p><div class="buttons">{links}</div></header>
<main class="container" id="main"><aside class="notice">This is a Capability-Aware website demonstration using an existing paper. For the original research, visit <a href="{p['original']}">{e(p['name'])}'s official website</a>.</aside>
<figure class="teaser"><video controls playsinline muted loop preload="metadata" aria-label="{e(p['name'])} research demonstration"><source src="{e(video)}" type="video/mp4">Your browser does not support this video. <a href="{e(video)}">Open the MP4</a>.</video>
<figcaption>{e(p['videoCaption'])} <a href="{e(video)}">Open video directly ↗</a></figcaption></figure>
<section class="content-section abstract"><h2>Overview</h2><p>{e(p['summary'])}</p></section>
<section class="content-section"><h2>Visual Results</h2><div class="gallery{' single' if len(p['figures'])==1 else ''}">{gallery}</div></section>
<section class="content-section"><h2>Presentation</h2><div class="video-embed"><iframe title="{e(p['name'])} original presentation" src="https://www.youtube-nocookie.com/embed/{p['youtube']}" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>
<p class="video-help">If the embedded player is unavailable, <a href="https://www.youtube.com/watch?v={p['youtube']}">watch on YouTube</a> or play the MP4 above.</p></section>
<section class="content-section"><div class="citation-heading"><h2>BibTeX</h2><button type="button" class="button secondary" data-copy-citation>Copy BibTeX</button></div><pre><code id="citation">{e(p['bibtex'])}</code></pre><p class="status" id="copy-status" aria-live="polite"></p></section>
<nav class="related" aria-label="Other projects"><a href="../">← All research projects</a><a href="../{other['slug']}/">Next demo: {e(other['name'])} →</a></nav></main>'''
    (folder/'index.html').write_text(shell(p['name']+' | Capability-Aware Demo', body, prefix, p['summary']))
    (folder/'citation.bib').write_text(p['bibtex']+'\n')

if __name__ == '__main__':
    build_home()
    for project in PROJECTS:
        build_project(project)
    print('Built homepage and', len(PROJECTS), 'project pages.')
