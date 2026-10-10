"""Build the minimal research homepage, placeholders, and archived demos."""
import json
from html import escape
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'projects.json').read_text())
PAPERS = json.loads((ROOT / 'papers.json').read_text())
VIDEOS = json.loads((ROOT / 'videos.json').read_text())
e = escape

def asset(url, prefix):
    return url if url.startswith(('https://', 'http://')) else prefix + url

def button(label, href, secondary=False):
    return f'<a class="button" href="{e(href)}">{e(label)}</a>'

def shell(title, body, prefix='', description='Locomotion, navigation, and manipulation toward physical intelligence.'):
    menu = ''.join(f'<a href="{prefix}{p["slug"]}/">{e(p["name"])}</a>' for p in PAPERS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}">
<link rel="stylesheet" href="{prefix}assets/site.css?v=paper-layout-v1"><script src="{prefix}assets/site.js?v=autoplay-v1" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<nav class="topnav" aria-label="Main navigation"><a class="home" href="{prefix or './'}" aria-label="Home"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 3 2 12h3v9h5v-6h4v6h5v-9h3L12 3z"/></svg></a><details class="project-menu"><summary>Research Projects <span aria-hidden="true">⌄</span></summary><div class="menu">{menu}</div></details></nav>
{body}
<footer><a href="https://github.com/Capability-Aware/Capability-Aware.github.io">Website source</a> · <a href="{prefix}CREDITS.md">Demo media credits</a></footer>
</body></html>'''

def build_home():
    cards = ''.join(f'<div class="video-card footage-card"><video controls autoplay muted loop playsinline preload="metadata" aria-label="{e(v["title"])}"><source src="{v["src"]}" type="video/mp4"><a href="{v["src"]}">{e(v["title"])}</a></video></div>' for v in VIDEOS)
    first = json.loads((ROOT / 'featured-video.json').read_text())
    papers = ''.join(f'<article class="paper-entry"><h3><a href="{p["slug"]}/">{e(p.get("title", p["name"]))}</a></h3><p>{e(p.get("status", "Coming soon."))}</p></article>' for p in PAPERS)
    home_links = json.loads((ROOT / 'links.json').read_text())
    links = ''.join(button(link['label'], link['url']) if link['url'] else
                    f'<span class="button" role="link" aria-disabled="true" title="Coming soon">{e(link["label"])}</span>'
                    for link in home_links)
    body = f'''<main id="main">
<header class="hero container"><h1>Capability Aware</h1>
<p class="authors"><a href="https://haozhangrobotics.github.io/">Hao Zhang</a></p><p class="affiliations">Westlake University</p>
<div class="buttons">{links}</div></header>
<figure class="teaser container" id="videos"><video id="showcase-video" controls playsinline muted loop preload="metadata" poster="{first['poster']}" aria-label="{e(first['title'])}"><source src="{first['src']}" type="video/mp4"><a href="{first['src']}">Open video</a></video><figcaption><span id="video-title">{e(first['title'])}</span> · <a id="video-direct" href="{first['src']}">Open video ↗</a></figcaption></figure>
<section class="video-strip" aria-label="Locomotion videos"><div class="carousel"><button class="carousel-arrow" data-scroll="-1" aria-label="Previous videos">‹</button><div class="video-track">{cards}</div><button class="carousel-arrow" data-scroll="1" aria-label="Next videos">›</button></div></section>
<section class="text-section" id="abstract"><h2>Abstract</h2><p>Capability Aware explores physical intelligence across locomotion, navigation, and manipulation. We study how robots can understand their capability boundaries, compose skills, and autonomously decide where to go and how to act—pushing the limits of what they can achieve in the physical world.</p></section>
<section class="text-section research" id="projects"><h2>Research Projects</h2>{papers}</section>
</main>'''
    (ROOT/'index.html').write_text(shell('Capability Aware', body))

def build_placeholder(p):
    folder = ROOT / p['slug']
    folder.mkdir(exist_ok=True)
    body = f'''<main id="main" class="placeholder-page"><header class="hero container"><h1>{e(p['name'])}</h1><p>Capability Aware</p></header><section class="text-section"><div class="empty-video"><span aria-hidden="true">▷</span><p>Video coming soon</p></div><h2>Coming soon</h2><p class="center">This project page is a placeholder. Paper, code, and video links will be added here.</p><div class="buttons">{button('← Capability Aware', '../')}</div></section></main>'''
    (folder/'index.html').write_text(shell(p['name']+' | Capability Aware', body, '../'))

def build_research(p):
    folder = ROOT / p['slug']
    folder.mkdir(exist_ok=True)
    links = ''.join(button(label, url) if url else
                    f'<span class="button unavailable" aria-disabled="true">{e(label)} <small>Coming soon</small></span>'
                    for label, url in p['links'].items())
    author_items = []
    for author in p['authors']:
        name = e(author['name'])
        if author.get('url'):
            name = f'<a href="{e(author["url"])}">{name}</a>'
        author_items.append(name + f'<sup>{e(author["affiliation"])}</sup>')
    authors = ' · '.join(author_items) if author_items else 'Authors to be announced'
    affiliations = '<br>'.join(e(line) for line in p['affiliations'].splitlines()) if p['affiliations'] else 'Affiliations to be announced'
    headline, subtitle = p['title'].split(': ', 1)
    def content(key, pending):
        return f'<p>{e(p[key])}</p>' if p[key] else f'<p class="pending-copy">{pending}</p>'
    def figure(key, placeholder):
        if not p.get(key):
            return f'<div class="figure-placeholder"><strong>{placeholder}</strong><span>Coming soon</span></div>'
        f = p[key]
        src = e(asset(f['src'], '../'))
        return f'<figure class="research-figure"><a href="{src}"><img src="{src}" alt="{e(f["alt"])}" loading="lazy"></a><figcaption>{e(f["caption"])} Click the figure to view full size.</figcaption></figure>'
    teaser = figure('overview_image', 'Project overview')
    video = p.get('video')
    if video:
        teaser += f'<figure class="research-video" id="project-video"><video controls playsinline muted loop preload="metadata" poster="{e(asset(video["poster"], "../"))}" aria-label="TempoLoco demonstration compilation"><source src="{e(asset(video["src"], "../"))}" type="video/mp4">Your browser does not support this video.</video><figcaption>{e(video["caption"])}</figcaption></figure>'
    else:
        teaser += '<div class="media-placeholder"><strong>Project video</strong><span>Coming soon</span></div>'
    body = f'''<main id="main" class="research-page">
<header class="hero paper-hero"><p class="paper-kicker">Capability Aware · Research</p>
<h1 class="research-title"><span>{e(headline)}:</span><span class="research-subtitle">{e(subtitle)}</span></h1>
<p class="authors{' pending-meta' if not p['authors'] else ''}">{authors}</p><p class="affiliations{' pending-meta' if not p['affiliations'] else ''}">{affiliations}</p>
<p class="publication-status">{e(p['status'])}</p><div class="buttons">{links}</div></header>
<div class="paper-teaser">{teaser}</div>
<nav class="section-nav" aria-label="Page sections"><a href="#abstract">Abstract</a><a href="#method">Method</a></nav>
<section class="paper-section" id="abstract"><h2>Abstract</h2>{content('abstract', 'Abstract coming soon.')}</section>
<section class="paper-section section-tinted" id="method"><div class="section-inner"><h2>Method Overview</h2>{content('method', 'Method details coming soon.')}{figure('method_image', 'Method figure')}</div></section>
<nav class="paper-back" aria-label="Back to project collection"><a href="../">← All research projects</a></nav>
</main>'''
    (folder/'index.html').write_text(shell(p['title']+' | Capability Aware', body, '../', p['title']))
    if p.get('legacy_slug'):
        old = ROOT / p['legacy_slug']
        old.mkdir(exist_ok=True)
        destination = '../' + p['slug'] + '/'
        (old/'index.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(p['name'])}</title><link rel="canonical" href="https://capability-aware.github.io/{e(p['slug'])}/"><meta http-equiv="refresh" content="0; url={e(destination)}"></head><body><p>This project has moved to <a href="{e(destination)}">{e(p['name'])}</a>.</p></body></html>''')

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
    for project in PAPERS:
        if project.get('type') == 'research':
            build_research(project)
        else:
            build_placeholder(project)
    for project in PROJECTS:
        build_project(project)
    print('Built homepage,', len(PAPERS), 'research/placeholder pages, and', len(PROJECTS), 'archived demos.')
