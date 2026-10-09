#!/usr/bin/env python3
"""Build the portfolio from small JSON catalogs and a documented Markdown subset.

Python standard library only. Generated HTML is committed for GitHub Pages.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://adenzhou1350.github.io"
SITE_DATE = "2026-10-09"
NAME = "周栩丞 · Aden Zhou"
EMAIL = "aden1350@outlook.com"


def github_pr_search(state=""):
    query = "is:pr is:public author:adenzhou1350 -user:adenzhou1350 sort:updated-desc"
    if state:
        query += f" is:{state}"
    return "https://github.com/search?" + urlencode({"q": query, "type": "pullrequests"})


def esc(value):
    return html.escape(str(value), quote=True)


def read_json(name):
    return json.loads((ROOT / "content" / name).read_text(encoding="utf-8-sig"))


def external(url, label, cls="text-link"):
    return f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{label}<span class="arrow" aria-hidden="true">↗</span><span class="sr-only">（新窗口）</span></a>'


def inline(text):
    tokens = []
    def code(match):
        tokens.append(f"<code>{esc(match.group(1))}</code>")
        return f"@@CODE{len(tokens)-1}@@"
    text = re.sub(r"`([^`]+)`", code, text)
    text = esc(text)
    def link(match):
        label, url = match.groups()
        raw = html.unescape(url)
        parsed = urlparse(raw)
        if parsed.scheme not in ("", "http", "https", "mailto") or raw.startswith("//"):
            raise ValueError(f"Unsupported content link: {raw}")
        return f'<a href="{esc(raw)}">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^\s)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    for number, value in enumerate(tokens):
        text = text.replace(f"@@CODE{number}@@", value)
    return text


CACHE_DEMO = '''<section class="cache-demo" data-cache-demo aria-label="输入身份与缓存交互实验">
<div class="demo-top"><div><h3>换了内容，缓存知道吗？</h3><p>逐步改变同一文件，比较两种缓存键。</p></div><span class="badge badge-neutral">教学模拟</span></div>
<noscript><p>开启 JavaScript 后可以操作演示；下方 Python 示例也完整解释了两种行为。</p></noscript>
<div class="demo-controls"><button class="primary" type="button" data-next>更新内容，保留文件名</button><button type="button" data-rename>只换文件名</button><button type="button" data-reset>重置</button></div>
<div class="demo-input">当前输入：<span data-input>screen.txt → button=save</span></div>
<div class="demo-columns"><div class="demo-result" data-path-result><div class="label">A / 以路径为键</div><div class="value" data-path-value>save</div><div class="state" data-path-state>初次计算</div></div>
<div class="demo-result right"><div class="label">B / 以完整内容为键</div><div class="value" data-content-value>save</div><div class="state" data-content-state>初次计算</div></div></div>
<div class="demo-live" data-demo-live aria-live="polite" aria-atomic="true">初始输入的预期结果是 save。</div>
<p class="demo-hint">只模拟字符串解析与 Map 缓存。没有模型调用、图像处理或性能测量。</p></section>'''


def markdown(source):
    """Headings, paragraphs, flat lists, fences, tables, blockquotes and links."""
    lines = source.lstrip("\ufeff").splitlines()
    output, toc = [], []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == "{{CACHE_DEMO}}":
            output.append(CACHE_DEMO)
            i += 1
            continue
        if line.startswith("!["):
            picture = re.fullmatch(r"!\[([^\]]+)\]\((/assets/images/[^\s)]+)\)", line)
            if not picture:
                raise ValueError("Images need descriptive alt text and a local /assets/images/ path")
            alt, url = picture.groups()
            asset = (ROOT / url.lstrip('/')).resolve()
            if not asset.is_relative_to(ROOT / 'assets/images') or not asset.is_file():
                raise ValueError(f"Invalid or missing image: {url}")
            output.append(f'<figure class="article-image"><img src="{esc(url)}" alt="{esc(alt)}" loading="lazy" decoding="async"><figcaption>{esc(alt)}</figcaption></figure>')
            i += 1
            continue
        if line.startswith("```"):
            language = line[3:].strip() or "text"
            code, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError("Unclosed fenced code block")
            output.append(f'<div class="code-wrap"><div class="code-label">{esc(language)}</div><button class="copy-code" type="button" aria-label="复制代码">复制</button><pre><code>{esc(chr(10).join(code))}</code></pre></div>')
            i += 1
            continue
        heading = re.match(r"^(#{2,3})\s+(.+)$", line)
        if heading:
            level, title = len(heading[1]), heading[2]
            anchor = f"section-{i+1}"
            output.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            if level == 2:
                toc.append((anchor, title))
            i += 1
            continue
        if line.startswith("# "):
            raise ValueError("Article h1 comes from catalog.json; body headings start at ##")
        if i + 1 < len(lines) and "|" in line and re.fullmatch(r"[\s|:\-]+", lines[i + 1]) and "---" in lines[i + 1]:
            cells = lambda row: [inline(cell.strip()) for cell in row.strip().strip("|").split("|")]
            headers = cells(line)
            table = '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th scope="col">{cell}</th>' for cell in headers) + '</tr></thead><tbody>'
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                row = cells(lines[i])
                if len(row) != len(headers):
                    raise ValueError("Table column count mismatch")
                table += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
                i += 1
            output.append(table + '</tbody></table></div>')
            continue
        listing = re.match(r"^(- |\d+\. )(.+)$", line)
        if listing:
            tag = "ul" if line.startswith("- ") else "ol"
            items = []
            while i < len(lines):
                item = re.match(r"^(- |\d+\. )(.+)$", lines[i].strip())
                if not item or (lines[i].strip().startswith("- ")) != (tag == "ul"):
                    break
                items.append(f'<li>{inline(item[2])}</li>')
                i += 1
            output.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
            continue
        if line.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            output.append('<blockquote><p>' + inline(' '.join(quote)) + '</p></blockquote>')
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3} |```|> |- |\d+\. |\{\{|!\[)", lines[i].strip()):
            paragraph.append(lines[i].strip())
            i += 1
        output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return '\n'.join(output), toc


def header(active):
    links = [("projects", "/projects/", "项目"), ("blog", "/blog/", "博客"), ("learn", "/learn/", "教学"), ("contributions", "/contributions/", "开源贡献"), ("about", "/about/", "关于")]
    nav = ''.join(f'<a href="{url}"{chr(32) + "aria-current=\"page\"" if key == active else ""}>{label}</a>' for key, url, label in links)
    return f'''<a class="skip" href="#main">跳到正文</a><header class="site-header"><div class="header-inner shell"><a class="brand" href="/" aria-label="周栩丞，首页"><span class="brand-symbol" aria-hidden="true">a.</span><span class="brand-name">Aden<span>周栩丞</span></span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">菜单 +</button><nav id="site-nav" class="site-nav" aria-label="主导航">{nav}<a class="github-link" href="https://github.com/adenzhou1350" target="_blank" rel="noopener noreferrer">GitHub ↗<span class="sr-only">（新窗口）</span></a></nav></div></header>'''


def footer():
    return f'''<footer class="site-footer"><div class="shell"><div class="footer-top"><a href="/" class="footer-signature">Built with curiosity.</a><div class="footer-links"><a href="mailto:{EMAIL}">工作联系 ↗</a><a href="https://github.com/adenzhou1350">GitHub ↗</a><a href="/feed.xml">RSS ↗</a><a href="/about/">关于本站</a></div></div><div class="footer-bottom"><span>© 2026 周栩丞 · ADEN ZHOU</span><span>AI INFRA / EMBODIED AGENTS / OPEN SOURCE</span></div></div></footer>'''


def page(title, description, body, path="/", active="", article=None):
    style_version = hashlib.sha256((ROOT / 'assets/site.css').read_text(encoding='utf-8').encode('utf-8')).hexdigest()[:12]
    canonical = BASE + path
    data = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE}
    if article:
        data = {"@context": "https://schema.org", "@type": "TechArticle", "headline": article["title"], "description": article["description"], "datePublished": article["date"], "dateModified": article.get("updated", article["date"]), "author": {"@type": "Person", "name": "周栩丞", "url": BASE + "/about/"}, "mainEntityOfPage": canonical}
    encoded_data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · {esc(NAME)}</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#f5f4ef"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="zh_CN"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css?v={style_version}"><link rel="alternate" type="application/rss+xml" title="Aden 的博客" href="/feed.xml"><script type="application/ld+json">{encoded_data}</script><script defer src="/assets/site.js"></script></head><body>{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''


def page_hero(kicker, title, description, number=""):
    return f'<div class="shell page-hero"><span class="page-number">{esc(number)}</span><p class="eyebrow orange">{esc(kicker)}</p><h1>{esc(title)}</h1><p class="intro">{esc(description)}</p></div>'


def section_head(kicker, title, url, label, desc=""):
    link = external(url, label) if url.startswith('https://') else f'<a class="text-link" href="{esc(url)}">{label}<span class="arrow" aria-hidden="true">↗</span></a>'
    return f'<div class="section-heading"><div class="section-title"><p class="eyebrow">{kicker}</p><h2>{title}</h2>{f"<p>{desc}</p>" if desc else ""}</div>{link}</div>'


def article_url(item):
    return f'/{item["section"]}/{item["slug"]}/'


def note_row(item, filterable=False):
    attrs = ''
    if filterable:
        search = ' '.join([item['title'], item['description'], *item['tags']])
        attrs = f' data-category="{esc(item["category"])}" data-search="{esc(search)}"'
    return f'''<a class="note-row" href="{article_url(item)}"{attrs}><time class="date" datetime="{item['date']}">{item['date'].replace('-', '.')}</time><div><h3>{esc(item['title'])}</h3><p>{esc(item['description'])}</p><div class="note-meta"><span>{esc(item['category'])}</span><span>约 {item['minutes']} 分钟</span></div></div><span class="note-arrow" aria-hidden="true">↗</span></a>'''


def system_art():
    icon = '<svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1"><path d="m18 5 13 7-13 7-13-7 13-7ZM5 18l13 7 13-7M5 24l13 7 13-7"/></svg>'
    return f'''<div class="systems-art" role="img" aria-label="三个工作层次：Agent应用、推理系统、验证与工具链"><div class="art-top"><span>THE SYSTEMS I WORK ON</span><span>FIG. 01</span></div><div class="art-stack"><div class="art-layer"><span class="art-index">01</span><div class="art-label"><strong>Agent 应用</strong><span>CONTEXT → TOOLS → ACTIONS</span></div>{icon}</div><div class="art-layer"><span class="art-index">02</span><div class="art-label"><strong>推理系统</strong><span>INPUTS → CACHE → SERVING</span></div>{icon}</div><div class="art-layer"><span class="art-index">03</span><div class="art-label"><strong>验证与工具链</strong><span>REPRODUCE → TEST → CONTRIBUTE</span></div>{icon}</div></div><div class="art-caption"><span>从应用行为，一路追到系统边界。</span><span class="art-cross" aria-hidden="true">＋</span></div></div>'''


def bonsai_feature(item):
    return f'''<section class="course-feature" aria-labelledby="bonsai-feature-title"><div class="course-feature-copy"><p class="eyebrow orange">FEATURED SERIES / BONSAI</p><h2 id="bonsai-feature-title">低比特大模型实战</h2><p class="course-feature-deck">从三值 QAT，到单卡推理。</p><p>沿着编码、训练、恢复与评测读懂一条压缩模型的工程链路。从几行 Python 开始，再走进真实的 MoE 实验。</p><div class="project-links"><a class="button" href="{article_url(item)}">从专题导读开始<span aria-hidden="true">→</span></a>{external(item['source_url'],'公开教学仓库')}</div></div><ol class="course-route"><li><span class="route-index">01</span><div><span class="route-resource">CPU / START SMALL</span><h3>先理解一个编码</h3><p>普通 Python 打包五个三值；Linux CPU 测试网格、梯度与恢复。</p></div></li><li><span class="route-index">02</span><div><span class="route-resource">35B MoE / 2×B300</span><h3>再走进真实训练</h3><p>准备教师、更新专家主权重，检查导出与恢复的每一步。</p></div></li><li><span class="route-index">03</span><div><span class="route-resource">122B MoE / RTX 5090</span><h3>把运行与质量分开核对</h3><p>低秩补偿与单卡推理案例。需指定 packed 权重，质量未达标。</p></div></li></ol></section>'''


def home(catalog, projects, contributions):
    posts = sorted([p for p in catalog if p['section'] == 'blog'], key=lambda p: p['date'], reverse=True)[:3]
    lessons = [p for p in catalog if p['section'] == 'learn']
    body = f'''<div class="shell"><section class="hero"><div><p class="eyebrow"><span class="status-dot"></span>AI INFRA · EMBODIED AGENTS</p><h1>让智能体，<br><em>真正跑起来。</em></h1><p class="hero-desc">我是周栩丞，Aden。做具身 Agent，也做它底下的推理系统。把模型、工具和状态接成可运行的链路，再用复现、测试和开源改进它。</p><div class="hero-actions"><a class="button" href="/projects/">看我构建的项目 <span aria-hidden="true">↗</span></a><a class="text-link" href="/blog/">阅读技术笔记<span class="arrow" aria-hidden="true">→</span></a></div><div class="hero-note"><span>深圳 · AI Agent 研发工程师</span><span>持续构建，公开记录</span></div></div>{system_art()}</section><div class="discipline-bar"><span>WORKING ACROSS</span><div class="discipline-items"><span>Agent Engineering</span><span>LLM Inference</span><span>Systems Reliability</span></div></div>
<section class="section">{section_head('01 / SELECTED PROJECTS','从想法，到能用的东西。','/projects/','全部项目')}<article class="featured-project"><div class="project-copy"><div class="project-kicker">FEATURED PROJECT <span class="badge">个人预览版</span></div><h3>栖伴 Nest</h3><p class="project-tagline">连接自己的模型，<br>把日常行动留在工作台。</p><p>待办、日历、资料查询与邮件草稿。可以查看执行记录，完成与否回到实际结果核对。</p><ul class="tag-list"><li>Python 3.10+</li><li>Agent</li><li>原生 Web</li><li>MIT</li></ul><div class="project-links">{external(projects[0]['url'],'查看项目')}<a class="text-link" href="/learn/nest-first-workflow/">上手教程<span class="arrow">→</span></a></div></div><div class="project-visual"><div class="window-bar"><i></i><i></i><i></i><span>NEST / PERSONAL WORKSPACE</span></div><img class="project-screen" src="/assets/images/nest-overview.jpg" alt="栖伴 Nest 工作台开发演示，包含待办、日程和本地草稿入口" width="1264" height="1054" loading="lazy"><p class="image-caption"><span>真实开发界面 · 合成示例</span><span>本地记录 / 自选模型</span></p></div></article><div class="project-secondary"><a class="project-tile project-tile-featured" href="/learn/bonsai-low-bit/"><span class="tile-number">02 / LOW-BIT LEARNING</span><h3>Bonsai 量化教学</h3><p>从 CPU 三值编码到 35B QAT，再读 122B MoE 单卡推理实验。把训练、恢复与质量评测的证据放在一起。</p><div class="tile-bottom"><span>PyTorch · 教学与研究</span><span aria-hidden="true">→</span></div></a><a class="project-tile" href="https://github.com/adenzhou1350/minimind-diffusion"><span class="tile-number">03 / MODEL EXPERIMENTS</span><h3>minimind-diffusion</h3><p>用小模型理解掩码扩散。把训练、采样和图文实验放进同一个可以阅读、运行的仓库。</p><div class="tile-bottom"><span>PyTorch · 学习实验</span><span aria-hidden="true">↗</span></div></a></div></section>
<section class="section notes-section">{section_head('02 / FIELD NOTES','把过程写下来。','/blog/','所有文章')}<div>{''.join(note_row(p) for p in posts)}</div></section></div>
<section class="learning-band"><div class="shell learning-grid"><div class="learning-intro"><p class="eyebrow">03 / LEARN BY BUILDING</p><h2>把复杂问题，<br>拆成能动手的一小步。</h2><p>从浏览器小实验、Agent 上手到低比特模型。先观察一个具体行为，再理解机制和验证方法。</p><a class="text-link" href="/learn/">进入教学专区<span class="arrow">↗</span></a></div><ol class="learning-list">{''.join(f'<li><a href="{article_url(item)}"><span class="num">0{i+1}</span><div><h3>{esc(item["title"])}</h3><p>{esc(item["category"])} · 约 {item["minutes"]} 分钟</p></div><span aria-hidden="true">↗</span></a></li>' for i,item in enumerate(lessons))}</ol></div></section>
<div class="shell"><section class="section">{section_head('04 / SELECTED CONTRIBUTIONS','让改进回到真实的系统。',github_pr_search(),'GitHub PR 记录')}<div class="contribution-grid">{''.join(f'<article class="contribution"><span class="repo">{esc(item["repo"])} / {item["number"]}</span><h3>{esc(item["title"])}</h3><p>{esc(item["description"])}</p>{external(item["url"],"查看已合并 PR")}</article>' for item in contributions[:3])}</div><div class="contribution-context"><p class="section-footnote">精选修复案例。更多公开 PR 与最新状态可在 GitHub 查看，搜索排除本人名下仓库。</p><a class="text-link" href="/contributions/">阅读精选案例<span class="arrow" aria-hidden="true">→</span></a></div></section><section class="contact-strip"><div><h2>有一个值得一起拆解的问题？</h2><p>欢迎交流 Agent 工程、推理系统与可复现的故障。</p></div><a class="button button-outline" href="mailto:{EMAIL}">工作联系<span aria-hidden="true">↗</span></a></section></div>'''
    return page("让智能体真正跑起来", "周栩丞 Aden Zhou 的技术作品集：具身 Agent、LLM 推理、Nest 工作台、Bonsai 低比特教学与工程复盘。", body)


def project_page(projects):
    cards = []
    for item in projects:
        guide = external(item['guide'], item['guide_label']) if item['guide'].startswith('http') else f'<a class="text-link" href="{item["guide"]}">{item["guide_label"]}<span class="arrow">→</span></a>'
        cards.append(f'''<article class="project-page-card"><p class="eyebrow">{esc(item['category'])}</p><h2>{esc(item['name'])}</h2><span class="badge">{esc(item['status'])}</span><p style="margin-top:20px">{esc(item['description'])}</p><ul class="tag-list">{''.join(f'<li>{esc(tag)}</li>' for tag in item['tags'])}</ul><p class="project-boundary">{esc(item['boundary'])}</p><div class="project-links">{external(item['url'],'GitHub 仓库')}{guide}</div></article>''')
    body = page_hero("PROJECTS / BUILD & EXPLORE", "在构建，也在探索。", "能使用的工具、仍在探索的实验，以及参与改进的开源项目。每个项目都说明现在能做什么。", f'{len(projects):02d} PROJECTS') + '<div class="shell page-content"><div class="project-page-grid">' + ''.join(cards) + '</div></div>'
    return page("项目", "Nest、Bonsai 低比特教学、minimind-diffusion、soul-generator 与 kernel_opt_agent：项目介绍、使用入口和当前边界。", body, "/projects/", "projects")


def blog_page(catalog):
    posts = sorted([item for item in catalog if item['section'] == 'blog'], key=lambda p: p['date'], reverse=True)
    categories = ['全部', *dict.fromkeys(item['category'] for item in posts)]
    filters = ''.join(f'<button class="filter-button" type="button" data-filter="{category}" aria-pressed="{str(i==0).lower()}">{category}</button>' for i,category in enumerate(categories))
    body = page_hero("BLOG / FIELD NOTES", "问题、实验，和后来的理解。", "记录 Agent 与推理系统中的具体问题：怎么复现、怎样修复、验证到了哪里。", f'{len(posts):02d} ARTICLES')
    body += f'<div class="shell page-content"><div class="filter-bar"><div class="filters" aria-label="文章分类">{filters}</div><label><span class="sr-only">搜索文章标题、简介或标签</span><input class="search-input" type="search" placeholder="搜索标题、问题或标签…" data-search></label></div><p class="results-status" data-results-status aria-live="polite">显示 {len(posts)} 篇文章</p><div data-content-list>{"".join(note_row(item,True) for item in posts)}</div><p class="empty-state" data-empty hidden>没有找到相关文章，试试其他关键词或选择“全部”。</p></div>'
    return page("博客", "关于多模态输入、缓存、Agent 工程与 kernel 工具链的技术复盘和开源笔记。", body, "/blog/", "blog")


def learning_page(catalog):
    lessons = [item for item in catalog if item['section'] == 'learn']
    featured = next((item for item in lessons if item['slug'] == 'bonsai-low-bit' and item.get('featured')), None)
    short_lessons = [item for item in lessons if item is not featured]
    body = page_hero("LEARNING / HANDS ON", "从一个小实验开始。", "从几行代码，到能核对的训练与推理。选择一条适合当前资源的路线，把原理、实现和实验记录接在一起。", f'{len(lessons):02d} GUIDES')
    cards = ''.join(f'<article class="learn-card"><p class="eyebrow orange">0{i+1} / {esc(item["category"])}</p><h2>{esc(item["title"])}</h2><p>{esc(item["description"])}</p><ul class="tag-list">{"".join(f"<li>{esc(tag)}</li>" for tag in item["tags"])}</ul><a class="text-link" href="{article_url(item)}">开始学习 · 约 {item["minutes"]} 分钟<span class="arrow">→</span></a></article>' for i,item in enumerate(short_lessons))
    body += '<div class="shell page-content">' + (bonsai_feature(featured) if featured else '') + '<div class="learn-cards">' + cards + '</div><div class="learning-note">想继续读模型代码？可以从 <a class="text-link" href="https://github.com/adenzhou1350/minimind-diffusion/blob/master/tests/test_model.py">minimind-diffusion 的模型测试 ↗</a> 开始。先检查形状与计算行为，再讨论训练后的生成效果。</div></div>'
    return page("教学", "Bonsai 低比特大模型专题、浏览器缓存实验和 Nest 个人 Agent 上手：从 CPU 原理到真实工程的学习路线。", body, "/learn/", "learn")


def article_page(item):
    content, toc = markdown((ROOT / item['source']).read_text(encoding='utf-8-sig'))
    label = '博客' if item['section'] == 'blog' else '教学'
    original = f'<a href="{esc(item["source_url"])}">相关原始记录 ↗</a>' if item.get('source_url') else ''
    body = f'''<div class="shell"><header class="article-top"><div class="breadcrumb"><a href="/">首页</a><span>/</span><a href="/{item['section']}/">{label}</a></div><p class="eyebrow orange">{esc(item['category'])} / {esc(item['kind'])}</p><h1>{esc(item['title'])}</h1><p class="article-deck">{esc(item['description'])}</p><div class="article-meta"><span>周栩丞 · Aden</span><time datetime="{item['date']}">{item['date']}</time><span>约 {item['minutes']} 分钟</span></div></header><div class="article-layout"><article class="article-body">{content}<div class="article-end"><p>本文含 AI 辅助整理；实验条件与验证范围见正文。</p>{original}<a href="mailto:{EMAIL}">讨论这个问题 ↗</a></div></article><aside class="article-aside"><p class="eyebrow">ON THIS PAGE / 目录</p><ol class="toc">{''.join(f'<li><a href="#{anchor}">{esc(title)}</a></li>' for anchor,title in toc)}</ol><p class="aside-note">{esc(item['kind'])}<br>把问题、方法和证据放在一起。</p></aside></div></div>'''
    return page(item['title'], item['description'], body, article_url(item), item['section'], item)


def contributions_page(items, path="/contributions/"):
    body = page_hero("OPEN SOURCE / CONTRIBUTIONS", "持续参与，持续改进。", "最新提交、讨论与合并状态，直接在 GitHub 查看。这里也保留一些代表性修复，记录问题、方法与验证。")
    body += f'''<div class="shell page-content"><section class="contribution-hub" aria-labelledby="github-activity-title"><div><p class="eyebrow orange">GITHUB / LATEST ACTIVITY</p><h2 id="github-activity-title">最新 PR 与合并状态</h2><p>公开 PR，排除本人名下仓库，按最近更新排序。</p></div><div class="contribution-actions">{external(github_pr_search(), '全部 PR', 'button')}{external(github_pr_search('merged'), '已合并', 'button button-outline')}{external(github_pr_search('open'), '进行中', 'button button-outline')}</div><p class="contribution-hub-note">个人项目、其他公开活动与贡献日历见 {external('https://github.com/adenzhou1350', 'GitHub 主页')}。</p></section><div class="section-heading"><div class="section-title"><p class="eyebrow">SELECTED CHANGES</p><h2>精选贡献解读</h2><p>挑几项具体修复，展开看改动解决了什么。</p></div></div>'''
    cards = []
    for item in items:
        cards.append(f'<article class="evidence-card"><p class="eyebrow orange">{esc(item["repo"])} / {item["number"]}</p><h2>{esc(item["title"])}</h2><p>{esc(item["description"])}</p><p class="meta">{esc(item["area"])} · 已合并 {item["merged"]}</p>{external(item["url"],"查看原始改动与验证")}</article>')
    body += '<div class="evidence-list">' + ''.join(cards) + '</div><p class="section-footnote">精选案例核对日期：2026-10-09；合并日期来自公开 PR 记录。后续进展请通过上方 GitHub 入口查看。</p><div class="learning-note"><strong>kernel_opt_agent：fork 扩展与持续研究</strong><br>围绕研究候选、实验编排、证据复用和环境治理持续改进。<a href="https://github.com/adenzhou1350/kernel_opt_agent">查看个人 fork ↗</a> · <a href="https://github.com/dasikuzi2/kernel_opt_agent">查看上游项目 ↗</a>。具体是否被上游接受，以每一条 PR 的状态为准。</div></div>'
    return page("开源贡献", "在 GitHub 查看最新公开 PR、已合并改动和进行中的讨论，并阅读 vLLM、Mooncake 等项目的精选修复案例。", body, path, "contributions")


def about_page():
    body = page_hero("ABOUT / ADEN ZHOU", "把一条链路做好。", "我是周栩丞，做 AI Agent 与大模型推理系统。喜欢从真实行为出发，把问题一路追到输入、状态和资源边界。")
    body += f'''<div class="shell page-content"><div class="about-layout"><section><h2>我关注的三个层次</h2><p>在应用侧，我关注语音交互、意图理解、工具调用与动作执行怎样接成可恢复的任务链。</p><p>在推理侧，我关注模型部署、多模态输入、KV Cache 和服务资源的组织方式。</p><p>在工程侧，我关注一个改动是否有可复现的触发条件、是否修复原问题，以及测试没有覆盖什么。公开项目和文章，是把这些过程留下来的方式。</p><ul class="tag-list"><li>AI Infra</li><li>具身 Agent</li><li>推理服务</li><li>系统可靠性</li></ul><div class="project-links"><a class="button" href="mailto:{EMAIL}">工作联系 ↗</a><a class="text-link" href="/assets/files/aden-zhou-xucheng-cv.pdf">查看中文简历 ↗</a></div></section><section><h2>经历与学习</h2><ol class="timeline"><li><span class="date">2026.03 — 至今</span><h3>自变量机器人</h3><p>AI Agent 研发工程师 · 具身任务链、工具调用、超时与消息同步。</p></li><li><span class="date">2025.03 — 2026.03</span><h3>华为 OD · 大模型平台</h3><p>软件开发工程师 · 模型部署流水线、Q4 权重量化、批处理调度与 KV Cache 调优。</p></li><li><span class="date">2023.02 — 2025.01</span><h3>悉尼大学</h3><p>硕士 · 网络与分布式系统</p></li><li><span class="date">2018.08 — 2022.12</span><h3>宾夕法尼亚州立大学</h3><p>学士 · 计算机工程</p></li></ol></section></div></div>'''
    return page("关于", "周栩丞 Aden Zhou：AI Agent 研发工程师，关注具身 Agent、LLM 推理和系统可靠性。", body, "/about/", "about")


def validate_catalog(catalog):
    seen = set()
    for item in catalog:
        if item['section'] not in ('blog', 'learn') or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', item['slug']):
            raise ValueError('Invalid section or slug')
        key = article_url(item)
        if key in seen:
            raise ValueError(f'Duplicate content path: {key}')
        seen.add(key)
        source = (ROOT / item['source']).resolve()
        if not source.is_relative_to(ROOT / 'content') or not source.is_file():
            raise ValueError(f'Invalid content source: {source}')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', item['date']):
            raise ValueError('Invalid content date')


def outputs():
    all_content, projects, contributions = read_json('catalog.json'), read_json('projects.json'), read_json('contributions.json')
    validate_catalog(all_content)
    catalog = [item for item in all_content if not item.get('draft', False)]
    out = {'index.html': home(catalog, projects, contributions), 'projects/index.html': project_page(projects), 'blog/index.html': blog_page(catalog), 'learn/index.html': learning_page(catalog), 'about/index.html': about_page(), 'contributions/index.html': contributions_page(contributions), 'details.html': contributions_page(contributions)}
    for item in catalog:
        out[article_url(item).strip('/') + '/index.html'] = article_page(item)
    out['404.html'] = page('页面未找到', '回到首页，继续阅读项目、博客与教学内容。', '<section class="shell not-found"><h1>404</h1><p>这个地址还没有内容。</p><a class="button" href="/">回到首页 →</a></section>', '/404.html')
    rss = []
    from datetime import datetime, timezone
    from email.utils import format_datetime
    for item in sorted([p for p in catalog if p['section'] == 'blog'], key=lambda p:p['date'], reverse=True):
        date = format_datetime(datetime.fromisoformat(item['date']).replace(tzinfo=timezone.utc), usegmt=True)
        rss.append(f'<item><title>{xml_escape(item["title"])}</title><link>{BASE + article_url(item)}</link><guid isPermaLink="true">{BASE + article_url(item)}</guid><description>{xml_escape(item["description"])}</description><pubDate>{date}</pubDate></item>')
    out['feed.xml'] = '<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel><title>Aden 的技术笔记</title><link>' + BASE + '/blog/</link><description>Agent、推理系统与开源工程记录</description><language>zh-CN</language>' + ''.join(rss) + '</channel></rss>'
    urls = ['/', '/projects/', '/blog/', '/learn/', '/contributions/', '/about/'] + [article_url(item) for item in catalog]
    dates = {article_url(item):item.get('updated', item['date']) for item in catalog}
    out['sitemap.xml'] = '<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{BASE+url}</loc><lastmod>{dates.get(url,SITE_DATE)}</lastmod></url>' for url in urls) + '</urlset>'
    out['robots.txt'] = f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n'
    out['.nojekyll'] = ''
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail when generated pages are out of date')
    args = parser.parse_args()
    rendered = outputs()
    stale = []
    for name, value in rendered.items():
        value = value.rstrip() + '\n' if value else ''
        target = ROOT / name
        if args.check:
            if not target.exists() or target.read_text(encoding='utf-8') != value:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(value, encoding='utf-8', newline='\n')
    if stale:
        raise SystemExit('Outdated generated files: ' + ', '.join(stale))
    count = sum(not item.get('draft', False) for item in read_json('catalog.json'))
    print(f'{"Verified" if args.check else "Built"} {len(rendered)} files; {count} articles / tutorials.')


if __name__ == '__main__':
    main()
