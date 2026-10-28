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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://adenzhou1350.github.io"
SITE_DATE = "2026-10-28"
NAME = "周栩丞 · Aden Zhou"
EMAIL = "aden1350@outlook.com"


def github_pr_search(state="", repository=""):
    scope = f"repo:{repository}" if repository else "-user:adenzhou1350"
    query = f"is:pr is:public author:adenzhou1350 {scope} sort:updated-desc"
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


def ternary_demo():
    trits = [-1, 0, 1, -1, 1]
    fields = ''.join(
        f'<label for="ternary-value-{index}"><span>位置 {index}</span><select id="ternary-value-{index}" data-trit>'
        + ''.join(f'<option value="{value}"{" selected" if value == initial else ""}>{"+1" if value == 1 else value}</option>' for value in (-1, 0, 1))
        + '</select></label>'
        for index, initial in enumerate(trits)
    )
    example = '''trits = [-1, 0, 1, -1, 1]
packed = sum((value + 1) * 3 ** i for i, value in enumerate(trits))
restored = [(packed // 3 ** i) % 3 - 1 for i in range(5)]

assert 0 <= packed < 256
assert restored == trits
print("packed byte:", packed)
print("binary:", format(packed, "08b"))
print("restored:", restored)'''
    article = BASE + '/learn/bonsai-low-bit/#ternary-demo'
    feedback = 'mailto:' + EMAIL + '?' + urlencode({
        'subject': 'Bonsai 三值编码小实验反馈',
        'body': f'文章：{article}\n当前输入：{trits}\n打包整数：183\n\n我卡在这里：\n',
    })
    return f'''<section class="ternary-demo" id="ternary-demo" data-ternary-demo aria-labelledby="ternary-demo-title">
<div class="ternary-demo-heading"><div><h3 id="ternary-demo-title">5 个三值，1 个字节</h3><p>改几个数，看看打包后能否原样拆回来。</p></div><button type="button" data-ternary-reset disabled>重置</button></div>
<noscript><p>开启 JavaScript 后可以修改选项；当前结果与 Python 示例仍可阅读和复制到本地运行。</p></noscript>
<fieldset class="ternary-inputs" data-ternary-inputs disabled><legend>选择输入（从位置 0 开始打包）</legend><div>{fields}</div></fieldset>
<p class="ternary-mapping">先将 −1、0、+1 映射成 0、1、2，再依次乘以 1、3、9、27、81 后相加。</p>
<p class="ternary-equation-live">当前计算：<span data-ternary-equation>0 × 1 + 1 × 3 + 2 × 9 + 0 × 27 + 2 × 81 = 183</span></p>
<dl class="ternary-results"><div><dt>打包整数</dt><dd data-ternary-packed>183</dd></div><div><dt>8 位二进制</dt><dd data-ternary-binary>10110111</dd></div><div class="ternary-restored"><dt>解包结果</dt><dd data-ternary-restored>[-1, 0, 1, -1, 1]</dd></div></dl>
<p class="ternary-verdict" data-ternary-verdict role="status" aria-live="polite" aria-atomic="true">往返一致：解包结果与这 5 个输入完全相同。</p>
<details class="ternary-code"><summary>查看并复制当前输入的 Python 示例</summary><div class="code-wrap"><div class="code-label">Python / 跟随当前输入更新</div><button class="copy-code" type="button" aria-label="复制当前输入的 Python 示例" disabled>复制</button><pre><code data-ternary-code>{esc(example)}</code></pre></div></details>
<p class="ternary-scope">这里只验证三值编码的打包与还原，不运行模型、不估算显存，也不测试量化后的回答质量。</p>
<div class="ternary-feedback"><a href="{esc(feedback)}" data-ternary-feedback data-email="{esc(EMAIL)}" data-article="{esc(article)}">这一步卡住了？写封邮件</a><span>会附上当前输入，供你修改后发送。</span></div>
</section>'''


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
        if line == "{{TERNARY_DEMO}}":
            output.append(ternary_demo())
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
    return f'''<footer class="site-footer"><div class="shell"><div class="footer-top"><a href="/" class="footer-signature">Aden / 周栩丞</a><div class="footer-links"><a href="mailto:{EMAIL}">工作联系 ↗</a><a href="https://github.com/adenzhou1350">GitHub ↗</a><a href="/feed.xml">RSS ↗</a><a href="/about/">关于本站</a></div></div><div class="footer-bottom"><span>© 2026 周栩丞 · ADEN ZHOU</span><span>AI INFRA / EMBODIED AGENTS / OPEN SOURCE</span></div></div></footer>'''


def page(title, description, body, path="/", active="", article=None, noindex=False):
    style_version = hashlib.sha256((ROOT / 'assets/site.css').read_text(encoding='utf-8').encode('utf-8')).hexdigest()[:12]
    script_version = hashlib.sha256((ROOT / 'assets/site.js').read_text(encoding='utf-8').encode('utf-8')).hexdigest()[:12]
    canonical = BASE + path
    robots_meta = '<meta name="robots" content="noindex, follow">' if noindex else ''
    data = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE}
    if article:
        data = {"@context": "https://schema.org", "@type": "TechArticle", "headline": article["title"], "description": article["description"], "datePublished": article["date"], "dateModified": article.get("updated", article["date"]), "author": {"@type": "Person", "name": "周栩丞", "url": BASE + "/about/"}, "mainEntityOfPage": canonical}
    encoded_data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · {esc(NAME)}</title><meta name="description" content="{esc(description)}">{robots_meta}<meta name="theme-color" content="#f5f4ef"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:locale" content="zh_CN"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css?v={style_version}"><link rel="alternate" type="application/rss+xml" title="Aden 的博客" href="/feed.xml"><script type="application/ld+json">{encoded_data}</script><script defer src="/assets/site.js?v={script_version}"></script></head><body>{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''


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
    return f'''<div class="systems-art" role="img" aria-label="三个工作层次：Agent应用、推理系统、验证与工具链"><div class="art-top"><span>THE SYSTEMS I WORK ON</span><span>FIG. 01</span></div><div class="art-stack"><div class="art-layer"><span class="art-index">01</span><div class="art-label"><strong>Agent 应用</strong><span>CONTEXT → TOOLS → ACTIONS</span></div>{icon}</div><div class="art-layer"><span class="art-index">02</span><div class="art-label"><strong>推理系统</strong><span>INPUTS → CACHE → SERVING</span></div>{icon}</div><div class="art-layer"><span class="art-index">03</span><div class="art-label"><strong>验证与工具链</strong><span>REPRODUCE → TEST → CONTRIBUTE</span></div>{icon}</div></div><div class="art-caption"><span>工具调用 / 模型服务 / 故障排查</span><span class="art-cross" aria-hidden="true">＋</span></div></div>'''


def bonsai_feature(item):
    return f'''<section class="course-feature" aria-labelledby="bonsai-feature-title"><div class="course-feature-copy"><p class="eyebrow orange">FEATURED SERIES / BONSAI</p><h2 id="bonsai-feature-title">Bonsai 量化教程</h2><p class="course-feature-deck">三值编码、QAT 和推理实验。</p><p>先在浏览器里改几个数，试试三值打包，再看训练、检查点恢复和推理。需要大显卡的实验会单独写明硬件要求。</p><div class="project-links"><a class="button" href="{article_url(item)}#ternary-demo">直接试三值编码<span aria-hidden="true">→</span></a><a class="text-link" href="{article_url(item)}">阅读导读<span class="arrow" aria-hidden="true">→</span></a>{external(item['source_url'],'公开教学仓库')}</div></div><ol class="course-route"><li><span class="route-index">01</span><div><span class="route-resource">BROWSER &amp; CPU / START SMALL</span><h3>三值编码与 CPU 测试</h3><p>先在浏览器里打包五个三值，再按需复制 Python 示例，或在 Linux CPU 上运行量化、梯度和恢复测试。</p></div></li><li><span class="route-index">02</span><div><span class="route-resource">35B MoE / 2×B300</span><h3>35B 全专家 QAT</h3><p>从两步控制学习教师、专家主权重和检查点恢复；长程训练已暂停。</p></div></li><li><span class="route-index">03</span><div><span class="route-resource">27B · 35B · 122B / RTX 5090</span><h3>三款模型下载与部署</h3><p>权重已公开，按各自加载器运行；速度口径不同，质量仍有限制。</p></div></li></ol></section>'''


def contributor_card(item, heading="h3"):
    return f'''<a class="contributor-card" href="{esc(github_pr_search('merged', item['repository']))}" target="_blank" rel="noopener noreferrer"><div class="contributor-meta"><span>{esc(item['area'])}</span><span class="contributor-arrow" aria-hidden="true">↗</span></div><{heading}>{esc(item['name'])}</{heading}><span class="contributor-repository">{esc(item['repository'])}</span><p>{esc(item['description'])}</p><div class="contributor-bottom"><span class="contributor-role">Contributor</span><span>查看我的已合并 PR <span aria-hidden="true">→</span></span></div><span class="sr-only">（新窗口）</span></a>'''


def recent_contributions(contributions, compact=False):
    names = {item['repository']: item['name'] for item in contributions['projects']}
    links = []
    for item in contributions.get('recent', []):
        date = datetime.fromisoformat(item['merged_at']).astimezone(timezone(timedelta(hours=8))).date()
        description = '' if compact else f'<p>{esc(item["description"])}</p>'
        links.append(f'''<li><a href="{esc(item['url'])}" target="_blank" rel="noopener noreferrer"><div class="recent-pr-meta"><span>{esc(names[item['repository']])}</span><time datetime="{date}">{date:%m.%d} 合并</time></div><strong>{esc(item['title'])}<span aria-hidden="true"> ↗</span></strong>{description}<span class="sr-only">PR #{item['number']}，新窗口</span></a></li>''')
    if not links:
        return ''
    heading = '<p class="recent-pr-label">近期改动</p>' if compact else '<h2 class="recent-pr-label">近期改动</h2>'
    return f'<div class="recent-contributions{ " recent-contributions-compact" if compact else "" }">{heading}<ul class="recent-pr-list">{"".join(links)}</ul></div>'


def home(catalog, projects, contributions):
    posts = sorted([p for p in catalog if p['section'] == 'blog'], key=lambda p: p['date'], reverse=True)[:2]
    project_by_repo = {item['repo']: item for item in projects}
    featured_contributors = [item for item in contributions['projects'] if item.get('featured')]
    contributor_links = ''.join(
        f'<a href="{esc(github_pr_search("merged", item["repository"]))}" target="_blank" rel="noopener noreferrer" aria-label="{esc(item["name"])}：查看我已合并的 PR（新窗口）"><span>{esc(item["name"])}</span><span aria-hidden="true">↗</span></a>'
        for item in featured_contributors
    )
    body = f'''<div class="portfolio-home shell">
<section class="hero portfolio-hero">
  <div class="hero-copy">
    <p class="eyebrow">ENGINEERING / OPEN SOURCE / NOTES</p>
    <h1>Aden <span class="hero-name-cn">周栩丞</span></h1>
    <p class="hero-role">AI Infra <span aria-hidden="true">/</span> 具身 Agent</p>
    <p class="hero-desc">在深圳做具身 Agent 研发，也做模型量化和推理实验。这里放公开代码、实验记录，以及参与过的开源改动。</p>
    <div class="hero-actions"><a class="button" href="#selected-work">看项目与实验 <span aria-hidden="true">↓</span></a><a class="text-link" href="/about/">关于我<span class="arrow" aria-hidden="true">→</span></a></div>
  </div>
  <nav class="work-index" aria-label="首页内容索引">
    <div class="work-index-heading"><span class="eyebrow">EXPLORE THE WORK</span><span>代码 / 实验 / 笔记</span></div>
    <a href="/blog/bonsai-5090-experiment/"><span class="work-index-number">01</span><div><strong>Bonsai · 低比特量化</strong><span>单卡 122B MoE，显存与质量实测</span></div><span aria-hidden="true">↗</span></a>
    <a href="/learn/jev-decision-model/"><span class="work-index-number">02</span><div><strong>Jev · 决策模型</strong><span>从 CPU 推箱子学候选动作打分</span></div><span aria-hidden="true">↗</span></a>
    <a href="/blog/"><span class="work-index-number">03</span><div><strong>工程笔记</strong><span>上游修复、量化实验与故障复盘</span></div><span aria-hidden="true">↗</span></a>
  </nav>
</section>
<section class="contributor-strip" id="open-source" aria-labelledby="home-contributor-title">
  <div class="contributor-strip-heading"><div><p class="eyebrow">CONTRIBUTOR TO</p><h2 id="home-contributor-title">参与贡献的开源项目</h2></div><a class="text-link" href="/contributions/">全部 {len(contributions['projects'])} 个项目<span class="arrow" aria-hidden="true">→</span></a></div>
  <div class="contributor-strip-links">{contributor_links}</div>
  {recent_contributions(contributions, compact=True)}
  <p class="section-footnote">点击项目查看我的已合并 PR · 项目名单核对于 {esc(contributions['checked_date'])}</p>
</section>
<section class="section home-work" id="selected-work">
  {section_head('01 / CODE &amp; EXPERIMENTS','代码与实验','/projects/','全部项目')}
  <div class="home-work-grid">
    <article class="work-card">
      <div class="work-media ternary-visual" role="img" aria-label="三值编码示意：五个三值编码可以打包进一个字节。这里只表示编码，不代表整个模型的位宽。">
        <span class="work-media-label">BONSAI / TERNARY ENCODING</span>
        <div class="ternary-values" aria-hidden="true"><span>−1</span><span>0</span><span>+1</span></div>
        <div class="ternary-equation" aria-hidden="true"><span>5 个三值编码</span><span>→</span><strong>1 byte</strong></div>
        <span class="work-media-caption">编码原理示意 · 实际模型还需尺度与其他权重</span>
      </div>
      <div class="work-card-copy"><p class="eyebrow orange">LOW-BIT MODELS / 教学与实验</p><h3>Bonsai 低比特量化</h3><p class="work-card-description">在浏览器里试三值打包，再看 QAT 与单卡推理。27B、35B、122B 权重已公开，附下载和部署步骤。</p><p class="work-card-boundary">三款速度与测试口径不同；量化质量仍有限制，本轮优化已停止。</p><div class="work-card-actions">{external(project_by_repo['bonsai-qat-teaching']['deployment'],'下载与部署')}<a class="text-link" href="/learn/bonsai-low-bit/#ternary-demo">先试三值编码<span class="arrow" aria-hidden="true">→</span></a>{external(project_by_repo['bonsai-qat-teaching']['url'],'GitHub')}</div></div>
    </article>
    <article class="work-card">
      <div class="work-media jev-visual"><div class="work-media-topline"><span class="work-media-label">JEV / DECISION LAB</span><span>CPU 可试玩</span></div><img src="/assets/images/jev-sokoban.jpg" width="1264" height="1206" loading="lazy" alt="仓库随附的 Jev 推箱子教学演示，完整保留棋盘、候选动作和训练前后评测说明"><a class="work-media-caption" href="/assets/images/jev-sokoban.jpg" target="_blank" rel="noopener noreferrer">固定教学实验 · 查看完整截图 ↗<span class="sr-only">（新窗口）</span></a></div>
      <div class="work-card-copy"><p class="eyebrow orange">DECISION MODELS / 动手课程</p><h3>Jev 决策模型</h3><p class="work-card-description">训练一个给候选动作打分的小模型，从 CPU 推箱子开始。附中文课程、可交互演示和训练评测代码。</p><p class="work-card-boundary">独立 Jev-style 教学实现，未复现 TypeSafe Jev 的专有训练方法。</p><div class="work-card-actions"><a class="text-link" href="/learn/jev-decision-model/">从 CPU 试玩开始<span class="arrow" aria-hidden="true">→</span></a>{external(project_by_repo['jev-decision-teaching']['url'],'GitHub')}</div></div>
    </article>
  </div>
</section>
<section class="section home-notes" id="field-notes">
  {section_head('02 / FIELD NOTES','工程笔记','/blog/','所有文章')}
  <div class="home-reading-layout"><div class="home-note-list">{''.join(note_row(p) for p in posts)}</div><aside class="home-learning" aria-labelledby="home-learning-title"><p class="eyebrow">LEARN BY TRYING</p><h3 id="home-learning-title">先在浏览器里试试</h3><p>文件内容改了，缓存还会返回旧结果吗？点几下就能看到，不需要模型或 GPU。</p><a class="button button-outline" href="/learn/cache-identity/">打开缓存小实验<span aria-hidden="true">→</span></a><a class="text-link" href="/learn/">浏览全部教程<span class="arrow" aria-hidden="true">↗</span></a></aside></div>
</section>
<section class="contact-strip home-contact"><div><p class="eyebrow">GET IN TOUCH</p><h2>聊聊具体的工程问题。</h2><p>具身 Agent、模型推理或开源协作，都可以发邮件联系。</p><p>邮箱：<span>{esc(EMAIL)}</span></p></div><a class="button" href="mailto:{EMAIL}">发邮件<span aria-hidden="true">↗</span></a></section>
</div>'''
    return page("AI Infra 与具身 Agent", "周栩丞 Aden Zhou 的公开代码与工程记录：Bonsai 低比特量化、Jev 决策模型教学、开源贡献和技术笔记。", body)


def project_page(projects):
    cards = []
    for item in projects:
        guide = external(item['guide'], item['guide_label']) if item['guide'].startswith('http') else f'<a class="text-link" href="{item["guide"]}">{item["guide_label"]}<span class="arrow">→</span></a>'
        if item.get('deployment'):
            guide = external(item['deployment'], '下载与部署') + guide
        cards.append(f'''<article class="project-page-card"><p class="eyebrow">{esc(item['category'])}</p><h2>{esc(item['name'])}</h2><span class="badge">{esc(item['status'])}</span><p style="margin-top:20px">{esc(item['description'])}</p><ul class="tag-list">{''.join(f'<li>{esc(tag)}</li>' for tag in item['tags'])}</ul><p class="project-boundary">{esc(item['boundary'])}</p><div class="project-links">{external(item['url'],'GitHub 仓库')}{guide}</div></article>''')
    body = page_hero("PROJECTS / BUILD & EXPLORE", "项目", "我做的工具和模型实验，也包括在其他开源项目上做的扩展。使用方法和当前进度都在各自的仓库里。", f'{len(projects):02d} PROJECTS') + '<div class="shell page-content"><div class="project-page-grid">' + ''.join(cards) + '</div></div>'
    return page("项目", "Jev 决策模型实战、Bonsai 低比特教学、minimind-diffusion 与 Agent 工具：项目介绍、使用方法和当前进度。", body, "/projects/", "projects")


def blog_page(catalog):
    posts = sorted([item for item in catalog if item['section'] == 'blog'], key=lambda p: p['date'], reverse=True)
    categories = ['全部', *dict.fromkeys(item['category'] for item in posts)]
    filters = ''.join(f'<button class="filter-button" type="button" data-filter="{category}" aria-pressed="{str(i==0).lower()}">{category}</button>' for i,category in enumerate(categories))
    body = page_hero("BLOG / FIELD NOTES", "技术笔记", "记录上游修复、模型量化和推理故障。问题怎么复现，改动有没有用，都尽量留下具体的测试和原始记录。", f'{len(posts):02d} ARTICLES')
    body += f'<div class="shell page-content"><div class="filter-bar"><div class="filters" aria-label="文章分类">{filters}</div><label><span class="sr-only">搜索文章标题、简介或标签</span><input class="search-input" type="search" placeholder="搜索标题、问题或标签…" data-search></label></div><p class="results-status" data-results-status aria-live="polite">显示 {len(posts)} 篇文章</p><div data-content-list>{"".join(note_row(item,True) for item in posts)}</div><p class="empty-state" data-empty hidden>没有找到相关文章，试试其他关键词或选择“全部”。</p></div>'
    return page("博客", "TileLang 上游修复、Bonsai 模型量化、GPU 工具链与缓存故障的技术笔记，附测试结果和原始记录。", body, "/blog/", "blog")


def learning_page(catalog):
    lessons = [item for item in catalog if item['section'] == 'learn']
    featured = next((item for item in lessons if item['slug'] == 'bonsai-low-bit' and item.get('featured')), None)
    short_lessons = [item for item in lessons if item is not featured]
    body = page_hero("LEARNING / HANDS ON", "动手试试", "从浏览器小实验、CPU 推箱子，到模型训练与量化。每篇先说明需要什么，再带你动手跑一遍。", f'{len(lessons):02d} GUIDES')
    cards = []
    for i, item in enumerate(short_lessons):
        preview = item['slug'] == 'jev-decision-model'
        media = '<figure class="learn-card-media"><img src="/assets/images/jev-sokoban.jpg" alt="Jev 推箱子本地演示，比较训练前后与随机策略，显示棋盘和候选动作概率" width="1264" height="1206" loading="lazy"><figcaption>仓库随附演示 · CPU 可运行</figcaption></figure>' if preview else ''
        cards.append(f'<article id="{esc(item["slug"])}" class="learn-card{ " learn-card-preview" if preview else "" }"><div><p class="eyebrow orange">0{i+1} / {esc(item["category"])}</p><h2>{esc(item["title"])}</h2><p>{esc(item["description"])}</p><ul class="tag-list">{"".join(f"<li>{esc(tag)}</li>" for tag in item["tags"])}</ul><a class="text-link" href="{article_url(item)}">开始学习 · 约 {item["minutes"]} 分钟<span class="arrow">→</span></a></div>{media}</article>')
    cards = ''.join(cards)
    body += '<div class="shell page-content">' + (bonsai_feature(featured) if featured else '') + '<div class="learn-cards">' + cards + '</div><div class="learning-note">想继续读模型代码？可以从 <a class="text-link" href="https://github.com/adenzhou1350/minimind-diffusion/blob/master/tests/test_model.py">minimind-diffusion 的模型测试 ↗</a> 开始。测试能帮助理解张量形状和计算过程；生成效果还要另行评估。</div></div>'
    return page("教学", "Jev 决策模型实战、Bonsai 量化教程与浏览器缓存实验，附环境要求与操作步骤。", body, "/learn/", "learn")


def article_page(item):
    content, toc = markdown((ROOT / item['source']).read_text(encoding='utf-8-sig'))
    label = '博客' if item['section'] == 'blog' else '教学'
    original = f'<a href="{esc(item["source_url"])}">相关原始记录 ↗</a>' if item.get('source_url') else ''
    dates = f'<span>发布于 <time datetime="{esc(item["date"])}">{esc(item["date"])}</time></span>'
    if item.get('updated') and item['updated'] != item['date']:
        dates += f'<span>更新于 <time datetime="{esc(item["updated"])}">{esc(item["updated"])}</time></span>'
    body = f'''<div class="shell"><header class="article-top"><div class="breadcrumb"><a href="/">首页</a><span>/</span><a href="/{item['section']}/">{label}</a></div><p class="eyebrow orange">{esc(item['category'])} / {esc(item['kind'])}</p><h1>{esc(item['title'])}</h1><p class="article-deck">{esc(item['description'])}</p><div class="article-meta"><span>周栩丞 · Aden</span>{dates}<span>约 {item['minutes']} 分钟</span></div></header><div class="article-layout"><article class="article-body">{content}<div class="article-end"><p>本文使用 AI 工具辅助整理。实验设置和测试结果见正文。</p>{original}<a href="mailto:{EMAIL}">讨论这个问题 ↗</a></div></article><aside class="article-aside"><p class="eyebrow">ON THIS PAGE / 目录</p><ol class="toc">{''.join(f'<li><a href="#{anchor}">{esc(title)}</a></li>' for anchor,title in toc)}</ol><p class="aside-note">{esc(item['kind'])}</p></aside></div></div>'''
    return page(item['title'], item['description'], body, article_url(item), item['section'], item)


def contributions_page(contributions, path="/contributions/"):
    items = contributions['projects']
    body = page_hero("OPEN SOURCE / CONTRIBUTOR TO", "参与贡献的开源项目", "从推理服务、GPU 算子到存储与 Python 工具。点击项目，查看我在该仓库已合并的 PR。", f'{len(items):02d} PROJECTS')
    body += f'''<div class="shell page-content">{recent_contributions(contributions)}<div class="contributor-intro"><p>按项目查看。下面每张卡片都链接到我在该仓库的公开合并记录。</p>{external(github_pr_search('merged'), '全部已合并 PR')}</div><div class="contributor-grid">{''.join(contributor_card(item, 'h2') for item in items)}</div><p class="section-footnote">项目名单核对于 {esc(contributions['checked_date'])}。卡片链接打开 GitHub 实时搜索，只显示我在对应仓库已合并的 PR；上方近期改动的日期为北京时间。</p><div class="contributor-more"><span>更多公开记录</span>{external(github_pr_search('open'), '进行中的 PR')}{external('https://github.com/adenzhou1350', 'GitHub 主页')}</div></div>'''
    return page("开源贡献", "周栩丞 Aden Zhou 参与贡献的开源项目：vLLM、SGLang、TensorRT-LLM、Triton、TileLang 等，附各仓库已合并 PR。", body, path, "contributions")


def about_page():
    body = page_hero("ABOUT / ADEN ZHOU", "关于我", "我是周栩丞，也叫 Aden，现在在深圳做 AI Agent 研发。")
    body += f'''<div class="shell page-content"><div class="about-layout"><section><h2>我平时做什么</h2><p>目前主要做具身 Agent，处理语音交互、意图理解、工具调用和动作执行。任务超时后怎么恢复、消息和执行状态怎么同步，也是工作中要解决的问题。</p><p>我也做过模型部署、权重量化、批处理调度和 KV Cache 调优。多模态输入与推理服务的资源管理，是我一直在关注的方向。</p><p>Jev、Bonsai 和 minimind-diffusion 是我的个人项目与实验。这里会记录遇到的故障、修复办法和测试结果；还没解决的问题也会写出来。</p><p>可以从两篇公开记录看起：<a class="text-link" href="/blog/tilelang-grid-barrier/">TileLang 同步修复</a>、<a class="text-link" href="/blog/bonsai-5090-experiment/">5090 量化实测</a>。</p><ul class="tag-list"><li>AI Infra</li><li>具身 Agent</li><li>推理服务</li><li>系统可靠性</li></ul><p>邮箱：<span>{esc(EMAIL)}</span></p><div class="project-links"><a class="button" href="mailto:{EMAIL}">工作联系 ↗</a><a class="text-link" href="/assets/files/aden-zhou-xucheng-cv.pdf">查看中文简历 ↗</a></div></section><section><h2>工作与教育</h2><ol class="timeline"><li><span class="date">2026.03 至今</span><h3>自变量机器人</h3><p>AI Agent 研发工程师 · 具身任务链、工具调用、超时与消息同步。</p></li><li><span class="date">2025.03 至 2026.03</span><h3>华为 OD · 大模型平台</h3><p>软件开发工程师 · 模型部署流水线、Q4 权重量化、批处理调度与 KV Cache 调优。</p></li><li><span class="date">2023.02 至 2025.01</span><h3>悉尼大学</h3><p>硕士 · 网络与分布式系统</p></li><li><span class="date">2018.08 至 2022.12</span><h3>宾夕法尼亚州立大学</h3><p>学士 · 计算机工程</p></li></ol></section></div></div>'''
    return page("关于", "周栩丞 Aden Zhou：AI Agent 研发工程师，关注具身 Agent、LLM 推理和系统可靠性。", body, "/about/", "about")


def withdrawn_page(item):
    title = "教程已撤下"
    reason = item.get('withdrawal_reason', '这篇内容已撤回，暂不提供阅读。')
    body = page_hero("PAUSED / ARCHIVE", title, reason)
    body += '<div class="shell page-content"><a class="button" href="/learn/">浏览其他教程 →</a></div>'
    return page(title, reason, body, article_url(item), noindex=True)


def validate_catalog(catalog):
    seen = set()
    for item in catalog:
        if item['section'] not in ('blog', 'learn') or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', item['slug']):
            raise ValueError('Invalid section or slug')
        if item.get('withdrawn') and not item.get('draft'):
            raise ValueError('Withdrawn content must remain a draft')
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
    all_content, projects, contributions = read_json('catalog.json'), read_json('projects.json'), read_json('contributor-projects.json')
    validate_catalog(all_content)
    catalog = [item for item in all_content if not item.get('draft', False)]
    out = {'index.html': home(catalog, projects, contributions), 'projects/index.html': project_page(projects), 'blog/index.html': blog_page(catalog), 'learn/index.html': learning_page(catalog), 'about/index.html': about_page(), 'contributions/index.html': contributions_page(contributions), 'details.html': contributions_page(contributions)}
    for item in catalog:
        out[article_url(item).strip('/') + '/index.html'] = article_page(item)
    for item in all_content:
        if item.get('withdrawn'):
            out[article_url(item).strip('/') + '/index.html'] = withdrawn_page(item)
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
