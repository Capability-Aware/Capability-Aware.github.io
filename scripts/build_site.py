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
    if p.get('demo'):
        if p['slug'] == 'paper2':
            build_demo_landing(p)
        else:
            build_placeholder_paper(p)
        return
    else:
        body = f'''<main id="main" class="placeholder-page"><header class="hero container"><h1>{e(p['name'])}</h1><p>Capability Aware</p></header><section class="text-section"><div class="empty-video"><span aria-hidden="true">▷</span><p>Video coming soon</p></div><h2>Coming soon</h2><p class="center">This project page is a placeholder. Paper, code, and video links will be added here.</p><div class="buttons">{button('← Capability Aware', '../')}</div></section></main>'''
    (folder/'index.html').write_text(shell(p['name']+' | Capability Aware', body, '../'))

def build_demo_landing(p):
    folder = ROOT / p['slug']
    folder.mkdir(exist_ok=True)
    videos = [
        ('低矮通道｜俯身穿越', 'media_stage/low_ceiling_success35_v16.mp4', 'result_low_clearance.jpg', 'terrain', '降低身体姿态，通过受限净空区域。'),
        ('稀疏梅花桩', 'media_stage/pillars_60mm_trot.mp4', 'result_pillars.jpg', 'terrain', '稀疏离散落脚点上的连续通过。'),
        ('中空不规则楼梯', 'media_stage/random_height_width_stairs_L0.mp4', 'result_stairs.jpg', 'terrain', '踏面尺寸与台阶高度变化的楼梯。'),
        ('窄梁行走', 'media_stage/beam_30cm_trot.mp4', 'result_beam.jpg', 'terrain', '沿窄梁保持连续步态并通过路线。'),
        ('0.5 m/s', 'media_stage/speed05_goals.mp4', 'result_speed05.jpg', 'motion', '低速目标下的四足落脚目标演示。'),
        ('1 m/s', 'media_stage/speed1_goals.mp4', 'result_speed1.jpg', 'motion', '1 m/s 目标速度演示。'),
        ('3 m/s', 'media_stage/speed3_goals.mp4', 'result_speed3.jpg', 'motion', '3 m/s 目标速度演示。'),
        ('5 m/s', 'media_stage/speed5_goals.mp4', 'result_speed5.jpg', 'motion', '5 m/s 目标速度与实际落脚演示。'),
        ('行走中切换步态', 'media_stage/combined_gait_transition_REVIEW_reference55_v8.mp4', 'result_gait_transition.jpg', 'motion', '在行走过程中依次请求不同步态。'),
        ('身体高度｜连续 20–68 cm', 'media_body_frontier_v1/body_height_CB_B_only.mp4', 'result_body_height.jpg', 'body', '连续高度变化；画面保留 C+B 与单 Body 对照。'),
        ('身体俯仰｜连续 ±28°', 'media_body_frontier_v1/body_pitch_CB_B_only.mp4', 'result_body_pitch.jpg', 'body', '连续俯仰变化；画面保留 C+B 与单 Body 对照。'),
        ('左右侧倾｜连续 ±40°', 'media_body_frontier_v1/body_roll_CB_B_only.mp4', 'result_body_roll.jpg', 'body', '连续侧倾变化；画面保留 C+B 与单 Body 对照。'),
        ('高度＋roll＋pitch 联合姿态', 'media_stage/body_combined.mp4', 'result_body_combined.jpg', 'body', '40 cm 高度，roll +5°、pitch −5°联合静态姿态。'),
    ]
    arm_tasks = [
        ('升高身体触达', 'arm_height', '高度变化时四足与机械臂协同触达；同屏对比固定 Body 与调用 Body。'),
        ('侧倾身体触达', 'arm_roll', '侧倾姿态下协同触达；同屏对比固定 Body 与调用 Body。'),
        ('俯仰身体触达', 'arm_pitch', '俯仰姿态下协同触达；同屏对比固定 Body 与调用 Body。'),
        ('组合姿态触达', 'arm_combined', '高度、roll 与 pitch 组合变化下协同触达；同屏对比两种 Body 配置。'),
        ('行走中触达', 'arm_moving_reach', '移动过程中完成四足行走与机械臂触达；同屏对比两种 Body 配置。'),
    ]
    videos.extend((title, f'media_arm_tasks/{slug}.mp4', f'result_{slug}.jpg', 'coordination', caption) for title,slug,caption in arm_tasks)
    ablation_titles = {
        'body': ('纯 Body（无臂）', '固定身体控制、不含机械臂的对照任务'),
        'contact': ('Contact 路线', '离散接触与落脚路线任务'),
        'joint': ('Body＋Contact 联合', '身体姿态与接触路线同时变化的任务'),
    }
    for suite,(suite_title,suite_caption) in ablation_titles.items():
        for variant,label in [('CB','完整 C+B'),('C_only','mask B｜C-only'),('B_only','mask C｜B-only')]:
            videos.append((f'{suite_title}｜{label}', f'media_stage_ablation/native_three_v2/{variant}_{suite}.mp4', f'result_ablation_{suite}_{variant}.jpg', 'ablation', f'{suite_caption}；当前展示已有阶段素材。'))
    def video_card(video):
        title,src,poster,category,caption = video
        return f'''<article class="p2-demo-card"><video controls playsinline muted preload="none" poster="../assets/videos/paper2/posters/{e(poster)}" aria-label="{e(title)}"><source src="../assets/videos/paper2/{e(src)}" type="video/mp4">Your browser does not support this video.</video><div class="p2-demo-copy"><h4>{e(title)}</h4><p>{e(caption)}</p></div></article>'''
    result_groups = [
        ('terrain', '挑战地形', '俯身穿越、稀疏梅花桩、不规则楼梯与窄梁。', 'terrain'),
        ('motion', '运动与步态', '0.5、1、3、5 m/s 速度目标，以及行走中的步态切换。', 'motion'),
        ('body', '身体姿态', '连续高度、俯仰、侧倾变化与多轴联合姿态。', 'body'),
        ('coordination', 'B+C 协同', '将合并展示中的五项四足—机械臂协同任务拆成独立视频卡片。', 'coordination'),
        ('ablation', '自我消融', '按 Body、Contact、Body＋Contact 三类任务查看已有 C+B、C-only 与 B-only 阶段素材。', 'ablation'),
    ]
    result_tabs = ''.join(f'<button class="p2-tab{" is-active" if i == 0 else ""}" id="tab-{key}" type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="panel-{key}" tabindex="{0 if i == 0 else -1}">{e(title)}</button>' for i,(key,title,_,_) in enumerate(result_groups))
    def result_panel(i, group):
        key,title,description,match = group
        hidden = ' hidden' if i else ''
        if key == 'ablation':
            groups = []
            for suite,(suite_title,_) in ablation_titles.items():
                cards = [video_card(video) for video in videos if video[3] == match and video[0].startswith(suite_title + '｜')]
                groups.append(f'<div class="p2-ablation-group"><h4>{e(suite_title)}</h4><div class="p2-clip-grid">{"".join(cards)}</div></div>')
            content = '<p class="p2-ablation-note">以下为当前已有的阶段对照视频；完整实验范围与指标请见 demo showcase。</p>' + ''.join(groups)
        else:
            cards = [video_card(video) for video in videos if video[3] == match]
            grid_class = ' p2-grid-4' if len(cards) == 4 else ''
            content = f'<div class="p2-clip-grid{grid_class}">{"".join(cards)}</div>'
        return f'<section class="p2-result-panel" id="panel-{key}" role="tabpanel" aria-labelledby="tab-{key}"{hidden}><h3>{e(title)}</h3><p>{e(description)}</p>{content}</section>'
    result_panels = ''.join(result_panel(i, group) for i,group in enumerate(result_groups))
    body = f'''<main id="main" class="research-page paper2-page">
<header class="hero paper-hero p2-hero"><p class="paper-kicker">Capability Aware · Interactive Research Preview</p>
<h1 class="research-title"><span>Paper 2</span><span class="research-subtitle">Research title in preparation</span></h1>
<p class="authors"><a href="https://haozhangrobotics.github.io/">Hao Zhang</a></p>
<p class="affiliations">Westlake University</p>
<p class="publication-status">Manuscript in preparation · Demonstrations available</p>
<p class="p2-intro">The paper is in preparation. Selected simulation demonstrations are available below.</p>
<div class="buttons"><a class="button" href="{e(p['demo'])}">Open the demo showcase</a><a class="button" href="#results">Browse results</a><a class="button" href="../">← Capability Aware</a></div></header>
<section class="p2-coming" aria-label="Upcoming real robot demonstration"><div class="empty-video p2-empty" role="img" aria-label="Real robot video coming soon"><span aria-hidden="true">▷</span><p>Video coming soon</p><small>Real-robot demonstration</small></div></section>
<nav class="section-nav p2-section-nav" aria-label="Paper sections"><a href="#abstract">Abstract</a><a href="#method">Method</a><a href="#results">Results</a></nav>
<section class="paper-section p2-abstract" id="abstract"><h2>Abstract</h2><p class="pending-copy">Abstract in preparation.</p></section>
<section class="paper-section section-tinted p2-method" id="method"><div class="section-inner"><h2>Method Overview</h2><div class="p2-method-placeholder"><span aria-hidden="true">◇</span><strong>Method diagram coming soon</strong><small>Framework overview in preparation</small></div></div></section>
<section class="p2-results" id="results"><h2>Results</h2><p class="p2-results-intro">按任务类别浏览仿真演示。点击下方标签切换视频组。</p><div class="p2-tabs" role="tablist" aria-label="Result categories">{result_tabs}</div>{result_panels}</section>
<section class="p2-footer-cta"><p>The full collection includes the current experiment pages and supporting details.</p><a class="button" href="{e(p['demo'])}">Open the demo showcase</a></section>
<nav class="paper-back" aria-label="Back to project collection"><a href="../">← All research projects</a></nav>
<script>
(()=>{{const tabs=[...document.querySelectorAll('.p2-tab')],panels=[...document.querySelectorAll('.p2-result-panel')];
const activate=tab=>{{tabs.forEach(t=>{{const active=t===tab;t.classList.toggle('is-active',active);t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1}});panels.forEach(p=>p.hidden=p.id!==tab.getAttribute('aria-controls'))}};
tabs.forEach((tab,index)=>{{tab.addEventListener('click',()=>activate(tab));tab.addEventListener('keydown',event=>{{let next=index;if(event.key==='ArrowRight')next=(index+1)%tabs.length;else if(event.key==='ArrowLeft')next=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;else return;event.preventDefault();tabs[next].focus();activate(tabs[next])}})}});}})();
</script>
</main>'''
    page = shell(p['name']+' | Capability Aware', body, '../', 'Interactive research preview and robot demonstrations from Capability Aware.')
    page = page.replace('site.css?v=paper-layout-v1', 'site.css?v=paper2-showcase-v6')
    (folder/'index.html').write_text(page)

def build_placeholder_paper(p):
    folder = ROOT / p['slug']
    folder.mkdir(exist_ok=True)
    body = f'''<main id="main" class="research-page paper2-page paper3-page">
<header class="hero paper-hero p2-hero"><p class="paper-kicker">Capability Aware · Interactive Research Preview</p>
<h1 class="research-title"><span>{e(p['name'])}</span><span class="research-subtitle">Research title in preparation</span></h1>
<p class="authors pending-meta">Authors in preparation</p><p class="affiliations pending-meta">Affiliations in preparation</p>
<p class="publication-status">Manuscript in preparation</p>
<p class="p2-intro">Project overview, method, and results are being prepared.</p>
<div class="buttons"><a class="button" href="{e(p['demo'])}">Open the demo showcase</a><a class="button" href="../">← Capability Aware</a></div></header>
<section class="p2-coming" aria-label="Upcoming project demonstration"><div class="empty-video p2-empty" role="img" aria-label="Project video coming soon"><span aria-hidden="true">▷</span><p>Video coming soon</p><small>Project demonstration</small></div></section>
<nav class="section-nav p2-section-nav" aria-label="Paper sections"><a href="#abstract">Abstract</a><a href="#method">Method</a><a href="#results">Results</a></nav>
<section class="paper-section p2-abstract" id="abstract"><h2>Abstract</h2><p class="pending-copy">Abstract in preparation.</p></section>
<section class="paper-section section-tinted p2-method" id="method"><div class="section-inner"><h2>Method Overview</h2><div class="p2-method-placeholder"><span aria-hidden="true">◇</span><strong>Method diagram coming soon</strong><small>Framework overview in preparation</small></div></div></section>
<section class="p2-results p3-results" id="results"><h2>Results</h2><p class="p2-results-intro">Results and selected demonstrations will be added here.</p><div class="p3-results-placeholder"><span aria-hidden="true">▷</span><strong>Results coming soon</strong></div></section>
<section class="p2-footer-cta"><p>Explore the current project demo.</p><a class="button" href="{e(p['demo'])}">Open the demo showcase</a></section>
<nav class="paper-back" aria-label="Back to project collection"><a href="../">← All research projects</a></nav>
</main>'''
    page = shell(p['name']+' | Capability Aware', body, '../', 'Paper 3 project page and demo showcase.')
    page = page.replace('site.css?v=paper-layout-v1', 'site.css?v=paper3-layout-v1')
    (folder/'index.html').write_text(page)

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
