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

def shell(title, body, prefix='', description='Capability-Aware pursues physical intelligence through understanding capability boundaries, composing skills, autonomous action, and expanding what robots can achieve.'):
    menu = ''.join(f'<a href="{prefix}{p["slug"]}/">{e(p["name"])} <small>· demo</small></a>' for p in PROJECTS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}">
<link rel="icon" type="image/png" href="{prefix}assets/brand/capability-aware-frontier.png">
<link rel="stylesheet" href="{prefix}assets/site.css?v=frontier-v2"><script src="{prefix}assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<div class="topbar"><nav class="container nav" aria-label="Main navigation">
<a class="brand" href="{prefix or './'}"><img src="{prefix}assets/brand/capability-aware-frontier.png" width="32" height="32" alt="">Capability-Aware</a><div class="nav-right">
<a href="{prefix or './'}#about">Vision</a>
<a href="{prefix or './'}#research">Research</a>
<details><summary>Projects</summary><div class="menu">{menu}</div></details>
<a class="github-nav" href="https://github.com/Capability-Aware">GitHub ↗</a></div></nav></div>
{body}
<footer><div class="container"><p><strong>Capability-Aware</strong> · Toward the frontier of physical intelligence</p>
<p><a href="https://github.com/Capability-Aware">GitHub</a> · <a href="{prefix}CREDITS.md">Demo media credits</a> · <a href="https://github.com/Capability-Aware/Capability-Aware.github.io">Website source</a></p></div></footer>
</body></html>'''

def build_home():
    cards = []
    for p in PROJECTS:
        links = button('Project page ↗', p['slug']+'/') + button('Paper', p['paper'], True) + button('Code', p['code'], True) + button('Video', 'https://www.youtube.com/watch?v='+p['youtube'], True)
        cards.append(f'''<article class="project">
<a class="thumbnail" href="{p['slug']}/"><img src="{e(p['image'])}" alt="{e(p['imageAlt'])}" width="660" height="430"><span class="image-label">Explore project ↗</span></a>
<div><span class="badge">DEMO PROJECT</span><h3><a href="{p['slug']}/">{e(p['title'])}</a></h3>
<p class="authors">{e(p['authors'])}</p><p class="venue">{e(p['venue'])}</p><p>{e(p['summary'])}</p><div class="buttons">{links}</div></div></article>''')
    body = f'''<header class="container hero frontier-hero">
<div class="hero-copy"><div class="eyebrow">A research agenda for physical intelligence</div><h1>Capability-Aware</h1>
<p class="frontier-headline">Toward the frontier<br>of physical intelligence.</p>
<p class="frontier-intro">Robots that understand what they can do, compose what they know, and discover what becomes possible.</p>
<div class="buttons">{button('Explore the vision', '#about')}{button('GitHub ↗', 'https://github.com/Capability-Aware', True)}</div></div>
<img class="frontier-logo" src="assets/brand/capability-aware-frontier.png" alt="Capability-Aware: interdependent geometric forms composing an open spatial boundary" width="320" height="320">
</header>
<main id="main" class="container">
<div class="manifesto-line"><span>Know the limits.</span><span>Compose capabilities.</span><span>Push the frontier.</span></div>
<section class="vision-section" id="about" aria-labelledby="about-title">
<div class="section-kicker">01 / The vision</div><h2 id="about-title">Understand the possible.<br>Make more possible.</h2>
<p class="vision-lead">We pursue physical intelligence through an explicit understanding of capability: what a robot can achieve, under which conditions, and how its abilities can be brought together to accomplish complex physical tasks.</p>
<p>Our long-term goal is for robots to autonomously work out where to go, how to act, and which capabilities to combine. That requires reasoning across movement, manipulation, contact, tool use, and collaboration—connecting individual skills to the structure of a task and the physical world around them.</p>
<p>Capability-Aware names this broader pursuit: giving robots a working understanding of the boundaries of physical tasks in the natural world, and the ability to discover how those boundaries change with a different body, a new skill, a tool, or a partner.</p>
<p class="chinese-statement" lang="zh-CN">认识能力边界，组合行动能力，拓展物理智能的极限。</p>
</section>
<section class="agenda-section" id="research" aria-labelledby="research-title">
<div class="section-kicker">02 / The research agenda</div>
<div class="heading"><h2 id="research-title">From individual abilities<br>to autonomous physical intelligence.</h2></div>
<div class="direction-grid frontier-directions">
<article class="direction"><span class="direction-number">I / UNDERSTAND</span><h3>Map capability boundaries.</h3><p>Represent what actions and tasks are achievable for a particular robot in a particular situation. Connect embodiment, control, environmental conditions, and uncertainty to predicted outcomes, performance, and failure modes.</p><p class="research-question">What can be done here, and under what conditions?</p></article>
<article class="direction"><span class="direction-number">II / COMPOSE</span><h3>Build capability from capability.</h3><p>Study how movement, manipulation, contact, tools, and cooperation combine into richer abilities. Reason about the prerequisites and consequences of each skill, and how their interaction opens new ways to complete a task.</p><p class="research-question">What becomes possible when abilities work together?</p></article>
<article class="direction"><span class="direction-number">III / ACT</span><h3>Turn understanding into autonomy.</h3><p>Connect task intent to decisions about where to go, what to do, and how to do it. Plan across long horizons, select and coordinate skills, and revise decisions as interaction reveals more about the world and the robot itself.</p><p class="research-question">How can a robot carry a goal through to completion?</p></article>
<article class="direction"><span class="direction-number">IV / EXTEND</span><h3>Push the achievable frontier.</h3><p>Use capability boundaries to identify where learning, control, composition, and physical interaction can unlock further performance. Pursue demanding regimes of agility, dexterity, precision, and efficiency, with reliability as part of the objective.</p><p class="research-question">How close can we get to the limits of physical performance?</p></article>
</div></section>
<section class="frontier-statement" aria-labelledby="frontier-title">
<div class="section-kicker">A boundary is a research frontier.</div><h2 id="frontier-title">Discover the limits.<br>Then advance them.</h2>
<p>Understanding a boundary tells us where to explore next. Our ambition is to approach the performance limits imposed by physics while expanding what robots can achieve through learning, capability composition, tools, and collaboration.</p>
</section>
<section class="approach-section current-section" aria-labelledby="approach-title">
<div class="section-kicker">03 / Where we begin</div><h2 id="approach-title">A first foothold:<br>capability-aware locomotion and navigation.</h2>
<p>Our current work starts with predicting the consequences of motion: where a robot may move, whether it can make progress, and where it may stall or fail. We investigate how embodied experience and pretrained visual knowledge can inform those predictions, and how explicit capability estimates can support trajectory selection.</p>
<p>This is an initial step toward the broader agenda. The same questions about feasibility, consequence, composition, and task completion guide our interest in manipulation and increasingly complex physical behavior.</p>
<div class="methods-note"><h3>Methods serve the research question.</h3><p>Methods such as FDM, MPPI, reinforcement learning, WAMs, and VLA models offer complementary ways to pursue this agenda. We study how to choose and combine them to improve a robot’s understanding of its capabilities and its ability to act on that understanding.</p></div>
</section>
<section class="publications-section" id="projects" aria-labelledby="projects-title">
<div class="heading"><h2 id="projects-title">Projects &amp; Publications</h2></div>
<p>Research project pages, papers, and code will be linked here as they are released.</p>
<details class="demo-projects"><summary>Explore the website demos <span>2 example project pages</span></summary>
<aside class="notice"><strong>Framework demo / 框架演示</strong> — The following published papers belong to their original authors. They demonstrate this website’s navigation and media, and are not Capability-Aware publications.</aside>
{''.join(cards)}</details></section></main>'''
    (ROOT/'index.html').write_text(shell('Capability-Aware | Physical Intelligence', body))

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
