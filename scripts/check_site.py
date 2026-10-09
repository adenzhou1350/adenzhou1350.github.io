#!/usr/bin/env python3
"""Check generated routes, fragment links, metadata and content disclosure gates."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import BASE, outputs, read_json, article_url


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.errors = [], set(), []
        self.h1 = 0
        self.title = False
        self.description = False
        self.canonical = False
    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                self.errors.append('Duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title = True
        if tag == 'meta' and attrs.get('name') == 'description': self.description = bool(attrs.get('content'))
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical = attrs.get('href', '').startswith(BASE)
        if tag == 'img' and 'alt' not in attrs: self.errors.append('Image missing alt')
        if tag == 'a' and attrs.get('target') == '_blank' and 'noopener' not in attrs.get('rel', ''): self.errors.append('External new-tab link lacks noopener')
        for field in ('href', 'src'):
            if attrs.get(field): self.links.append(attrs[field])


def main():
    failures, docs = [], {}
    for relative, rendered in outputs().items():
        target = ROOT / relative
        if not target.exists():
            failures.append(f'Missing generated file: {relative}')
            continue
        expected = rendered.rstrip() + '\n' if rendered else ''
        if target.read_text(encoding='utf-8') != expected:
            failures.append(f'Stale generated file: {relative}')
        if target.suffix == '.html':
            doc = Document()
            doc.feed(target.read_text(encoding='utf-8'))
            docs[target.resolve()] = doc
            if doc.h1 != 1 or not all((doc.title, doc.description, doc.canonical)):
                failures.append(f'Heading or SEO metadata missing: {relative}')
            failures.extend(f'{relative}: {error}' for error in doc.errors)
    for path, doc in docs.items():
        for link in doc.links:
            url = urlparse(link)
            if url.scheme or url.netloc:
                continue
            destination = ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent / unquote(url.path) if url.path else path
            if destination.is_dir(): destination /= 'index.html'
            destination = destination.resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                failures.append(f'{path.relative_to(ROOT)}: broken local link {link}')
            elif url.fragment and destination in docs and unquote(url.fragment) not in docs[destination].ids:
                failures.append(f'{path.relative_to(ROOT)}: missing anchor {link}')
    for filename in ('feed.xml', 'sitemap.xml'):
        ElementTree.parse(ROOT / filename)
    projects = read_json('projects.json')
    kernel = next(project for project in projects if project['repo'] == 'kernel_opt_agent')
    if 'fork' not in kernel['boundary'].lower(): failures.append('Kernel project fork attribution missing')
    case = (ROOT / 'blog/image-cache-identity/index.html').read_text(encoding='utf-8')
    for fact in ('6/8', '0.0625', '0.125', '合成状态', '不是客户生产案例'):
        if fact not in case: failures.append('Case boundary missing: ' + fact)
    html_pages = '\n'.join(path.read_text(encoding='utf-8') for path in docs)
    if 'llm-inference-step-by-step' in html_pages or '25 章' in html_pages:
        failures.append('Private course may have been advertised as public')
    for item in read_json('catalog.json'):
        if item.get('draft') and article_url(item) in html_pages:
            failures.append('Draft linked from published page: ' + item['slug'])
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(docs)} HTML pages, local links and anchors, RSS/sitemap XML, metadata and content boundaries.')


if __name__ == '__main__':
    main()
