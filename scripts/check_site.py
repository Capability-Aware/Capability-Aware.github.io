"""Check generated local pages, anchors, media references, and demo labels."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
projects = json.loads((ROOT/'projects.json').read_text())

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.links, self.ids, self.videos = path, [], set(), 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {self.path}: {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag == 'video':
            self.videos += 1
            assert 'controls' in attrs and 'playsinline' in attrs
        for key in ['href', 'src']:
            if attrs.get(key):
                self.links.append(attrs[key])

paths = [ROOT/'index.html'] + [ROOT/p['slug']/'index.html' for p in projects]
pages = {p.resolve(): Page(p) for p in paths}
for path, page in pages.items():
    assert 'demo' in path.read_text().lower(), 'Missing demo disclosure'
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            assert url.scheme in ['https', 'http'], f'Unexpected protocol: {link}'
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if target.is_dir():
            target /= 'index.html'
        assert target.exists(), f'Missing local target: {path.name}: {link}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'Missing anchor: {link}'
    if path != (ROOT/'index.html').resolve():
        assert page.videos == 1
    print('PASS', path.relative_to(ROOT))

assert (ROOT/'assets/nerfies-teaser.mp4').stat().st_size > 100000
print('PASS local MP4, project navigation, local assets, anchors, and demo disclosures')
