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

def shell(title, body, prefix='', description='Capability-Aware: research on embodied consequence prediction, visual priors, and robot planning grounded in predicted capabilities.'):
    menu = ''.join(f'<a href="{prefix}{p["slug"]}/">{e(p["name"])} <small>· demo</small></a>' for p in PROJECTS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}">
<link rel="icon" type="image/png" href="{prefix}assets/brand/capability-aware-avatar.png">
<link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<div class="topbar"><nav class="container nav" aria-label="Main navigation">
<a class="brand" href="{prefix or './'}"><img src="{prefix}assets/brand/capability-aware-avatar.png" width="32" height="32" alt="">Capability-Aware</a><div class="nav-right">
<a href="{prefix or './'}#about">About</a>
<a href="{prefix or './'}#research">Research</a>
<details><summary>Projects</summary><div class="menu">{menu}</div></details>
<a class="github-nav" href="https://github.com/Capability-Aware">GitHub ↗</a></div></nav></div>
{body}
<footer><div class="container"><p><strong>Capability-Aware</strong> · Embodied consequence prediction and planning</p>
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
    body = f'''<header class="container hero research-hero">
<img class="hero-logo" src="assets/brand/capability-aware-avatar.png" alt="Capability-Aware: a capability envelope surrounding a forward path" width="112" height="112">
<div class="eyebrow">Embodied intelligence · Robot learning</div><h1>Capability-Aware</h1>
<p class="intro">Understanding what a robot can do,<br class="wide-only"> and planning with that knowledge.</p>
<p class="hero-question">What will happen if this robot takes this action here?</p>
<div class="buttons">{button('Our research', '#research')}{button('GitHub ↗', 'https://github.com/Capability-Aware', True)}</div></header>
<main id="main" class="container">
<section class="about-section" id="about" aria-labelledby="about-title">
<div class="section-kicker">Our perspective</div><h2 id="about-title">Why Capability-Aware?</h2>
<p>Capability is a relationship between a robot, its controller, its current state, and the environment. The same route can lead to different outcomes for different robots—or for the same robot under different conditions.</p>
<p>We study how to make that relationship explicit and useful for decision-making. Given a candidate action, a robot should be able to anticipate its motion, the progress it may make, and the possibility of getting stuck or failing. These predicted consequences form a queryable model of what the robot can do in context.</p>
<blockquote>Choose actions that advance the task while respecting the robot’s predicted capability limits.</blockquote>
<p class="chinese-statement" lang="zh-CN">感知自身能力，预测行动后果，在能力边界内推进任务。</p>
</section>
<section class="agenda-section" id="research" aria-labelledby="research-title">
<div class="heading"><h2 id="research-title">Research Directions</h2><span>Our research agenda</span></div>
<div class="direction-grid">
<article class="direction"><span class="direction-number">01 / EXPERIENCE</span><h3>Learn from the body</h3><p>Model the consequences of candidate actions using visual observations, proprioceptive history, and embodied experience. Our focus is on predictions of motion, task progress, stalling, and failure that a planner can inspect and compare.</p></article>
<article class="direction"><span class="direction-number">02 / GENERALIZATION</span><h3>Reason beyond experience</h3><p>Investigate how pretrained visual knowledge can complement experience-based prediction in unfamiliar scenes. The aim is to improve consequence estimates while remaining grounded in the robot’s actual embodiment and accounting for uncertainty.</p></article>
<article class="direction"><span class="direction-number">03 / DECISION</span><h3>Plan with capability</h3><p>Use predicted consequences to compare candidate trajectories. We study how to distinguish physical feasibility, failure risk, and task progress, and how local motion choices can remain consistent with a longer-horizon navigation goal.</p></article>
</div></section>
<section class="approach-section" aria-labelledby="approach-title">
<div class="section-kicker">Connecting prediction to action</div><h2 id="approach-title">From embodied experience to informed decisions</h2>
<p>Our current direction brings experience-based motion prediction together with pretrained visual priors and sampling-based planning. Keeping prediction and decision-making explicit lets us ask two separate questions: how accurately can a robot anticipate an outcome, and how should that outcome influence its next action?</p>
<ol class="research-flow"><li><strong>Observe</strong><span>Scene and robot state</span></li><li><strong>Predict</strong><span>Candidate action consequences</span></li><li><strong>Evaluate</strong><span>Capability, risk, and progress</span></li><li><strong>Act &amp; replan</strong><span>Update from new observations</span></li></ol>
<p class="research-note">We begin with locomotion and navigation, with a broader interest in capability-aware decision-making across embodied tasks.</p>
</section>
<section class="publications-section" id="projects" aria-labelledby="projects-title">
<div class="heading"><h2 id="projects-title">Projects &amp; Publications</h2></div>
<p>Research project pages, papers, and code will be linked here as they are released.</p>
<details class="demo-projects"><summary>Explore the website demos <span>2 example project pages</span></summary>
<aside class="notice"><strong>Framework demo / 框架演示</strong> — The following published papers belong to their original authors. They demonstrate this website’s navigation and media, and are not Capability-Aware publications.</aside>
{''.join(cards)}</details></section></main>'''
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
