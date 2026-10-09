#!/usr/bin/env python3
"""Create a draft Markdown article and its catalog entry without publishing it."""
import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section', choices=('blog', 'learn'))
    parser.add_argument('slug', help='Lowercase words separated by hyphens')
    parser.add_argument('title')
    parser.add_argument('--description', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.slug):
        parser.error('slug must contain lowercase words separated by hyphens')
    catalog_path = ROOT / 'content/catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8-sig'))
    folder = 'posts' if args.section == 'blog' else 'learn'
    source = f'content/{folder}/{args.slug}.md'
    target = ROOT / source
    if target.exists() or any(item['slug'] == args.slug and item['section'] == args.section for item in catalog):
        parser.error('This content already exists; nothing was overwritten')
    item = {'slug': args.slug, 'section': args.section, 'title': args.title, 'description': args.description, 'category': '技术笔记' if args.section == 'blog' else '动手教程', 'date': date.today().isoformat(), 'minutes': 5, 'tags': [], 'source': source, 'kind': '技术笔记' if args.section == 'blog' else '上手教程', 'draft': True}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('写下这篇内容要回答的具体问题。\n\n## 问题与条件\n\n## 方法与步骤\n\n## 结果与边界\n\n## 来源\n', encoding='utf-8', newline='\n')
    catalog.append(item)
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Draft created: {source}')
    print('After review, set draft to false in content/catalog.json, then build and verify.')


if __name__ == '__main__':
    main()
