# Aden / 周栩丞 · 个人网站

AI Infra 与具身 Agent 的作品集、博客和教学空间。

线上入口：https://adenzhou1350.github.io/

- `/projects/`：Nest、Jev 决策模型实战、Bonsai 低比特教学、模型实验、Agent 工具与 fork 扩展。
- `/blog/`：技术复盘，支持分类和关键词筛选。
- `/learn/`：Jev 决策模型、Bonsai 低比特专题、Nest 入门和浏览器交互实验。
- `/learn/jev-decision-model/`：从随附的 CPU 推箱子策略进入候选打分、训练和页面按钮选择。
- `/learn/bonsai-low-bit/`：从纯 Python 三值打包，进入 Linux CPU 测试、35B QAT 与 122B MoE 单卡推理的专题导读。
- `/contributions/`：GitHub 最新 PR、已合并与进行中入口，以及精选修复案例。首页贡献区直接链接 GitHub 搜索。
- `/about/`：公开职业经历、教育和工作联系。

纯静态 HTML/CSS/JavaScript；Python 标准库生成内容页。访问网站不需要 Python、账号或后台。保留旧 `details.html` 地址，以便已有分享链接继续可用。

## 本地预览

构建工具使用 Python 3.12+（本次在 Windows 原生 Python 3.14 验证）：

```powershell
python -X utf8 scripts/build_site.py
python -X utf8 scripts/check_site.py
python -m http.server 18491 --bind 127.0.0.1
```

打开 http://127.0.0.1:18491 。请通过 HTTP 预览，站内根路径不适合直接双击 HTML。不会启动 WSL、Docker 或模型。

## 写一篇文章

```powershell
python -X utf8 scripts/new_content.py blog my-first-note "文章标题" --description "一句话说明解决了什么问题"
```

新条目默认 `draft: true`，不会出现在生成的页面、RSS 或站点地图里。

1. 编辑 `content/posts/my-first-note.md`，填写实际正文。
2. 编辑 `content/catalog.json` 中该条目的分类、标签、日期和预估阅读时间；检查内容后将 `draft` 改为 `false`。
3. 运行构建与检查，浏览本地效果后一起提交 Markdown、目录及生成的 HTML。

教学内容把命令中的 `blog` 换成 `learn`。同名内容不会被覆盖。已发布文章撤回时，除了改为草稿，还需从 Git 删除对应的生成目录，避免旧地址继续访问。

当前内容目录：

| 栏目 | 文章 / 专题 | 源文件 |
|---|---|---|
| 博客 | 截图更新了，为什么评分还是旧的？ | `content/posts/image-cache-identity.md` |
| 博客 | ptxas 解析器混读了两份 kernel 报告 | `content/posts/kernel-report-boundaries.md` |
| 教学专题 | Jev 决策模型：从推箱子学候选打分 | `content/learn/jev-decision-model.md` |
| 教学专题 | Bonsai 量化入门：三值编码、QAT 和单卡推理 | `content/learn/bonsai-low-bit.md` |
| 交互教程 | 文件名没变，缓存为什么会返回旧结果？ | `content/learn/cache-identity.md` |
| 上手教程 | Nest 上手：添加待办、修改记录和写邮件草稿 | `content/learn/nest-first-workflow.md` |

Bonsai 在目录中设置 `featured: true`，由教学页的专题组件呈现；实验状态以公开仓库为准。项目页计数按 `content/projects.json` 的实际条目生成。

```powershell
python -X utf8 scripts/build_site.py
python -X utf8 scripts/check_site.py
git diff --check
```

现有 GitHub Pages 从已提交的静态文件发布；只改 Markdown 而不重建不会更新正文。推送到网站的发布分支后，以线上页面实际内容确认完成。

## 文案约定

项目先说用途和当前能做什么，文章直接写遇到的问题。栏目标题用内容名称，少用口号、排比和抽象总结。可以用第一人称，但不要编造经历、客户或成果。

编辑时保留代码、链接、实验数字和使用限制。AI 辅助整理的说明照常保留。2026-10-10 的文案修订参考了 [Humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md)，按段落重写后再检查事实是否变化。

## 支持的正文格式

- `##`、`###` 标题；一级标题由目录元数据提供。
- 普通段落、非嵌套有序或无序列表、链接、粗体与行内代码。
- 带语言名的三反引号代码块、引用块和简单 Markdown 表格。
- 独占一行的图片：`![图片说明](/assets/images/example.jpg)`。先把图片放入 `assets/images/`；说明同时用作替代文本和图注。暂不支持外链图片。
- `{{CACHE_DEMO}}` 是本站缓存教学实验的专用组件标记。

HTML 源码会被转义，正文不运行任意 HTML 或 JavaScript。复制代码需要浏览器允许剪贴板写入；失败时仍可手动选择代码。

## 文件结构

```text
content/catalog.json          文章和教程目录
content/posts/*.md            博客正文
content/learn/*.md            教学正文
content/projects.json         项目事实、边界与链接
content/contributions.json    精选贡献与合并日期
scripts/build_site.py         模板与静态内容生成
scripts/new_content.py        新建草稿
scripts/check_site.py         链接、锚点、元数据和内容边界检查
assets/site.css               当前设计与响应式布局
assets/site.js                菜单、筛选、复制、教学交互
assets/images/                已公开项目的开发演示图片
```

`index.html`、各栏目及内容目录、`details.html`、`feed.xml`、`sitemap.xml` 由构建生成；不要把新文章只写进生成文件。

## 内容来源与范围

- 项目依据对应公开仓库。Nest 标注个人预览版，Bonsai 标注公开教学与持续实验，minimind-diffusion 标注学习实验，kernel_opt_agent 标注 fork 扩展。
- Bonsai 导读依据公开仓库 `7248f7f` 的 README、METHOD、REPRODUCING 与实验索引。35B 全专家 QAT 与 122B 低秩补偿分开介绍，保留 MoE、资源、权重和质量边界。
- Bonsai 的网页编码小实验只使用 Python 标准功能。仓库 CPU 检查点测试使用 POSIX 目录同步，教程按 Linux CPU 路线说明；没有宣称 Windows 原生支持或完整 122B 一键复刻。
- 精选贡献链接与合并日期已于 2026-10-09 核对。最新活动通过 GitHub 搜索查看，限定作者为 `adenzhou1350`、公开 PR、排除本人名下仓库，按最近更新排序；已合并与进行中分别用 `is:merged` 和 `is:open`。网站不缓存完整数量，个人项目及其他公开活动另链 GitHub 主页；原来的 `oss-stats.json` 仅保留为历史数据。
- Jev 导读依据公开仓库 `a04dfb4` 的三节课、安装说明与实验记录。推箱子为独立 CNN；页面按钮使用冻结的 Qwen3.5-0.8B 与共享打分头，保留模型快照、合成数据和评测范围。演示截图取自该仓库 `docs/assets/demo-sokoban.jpg`，按项目 MIT 许可使用；不是本站在线模型服务。
- Nest 图片取自其公开仓库 `docs/assets/overview.jpg`，使用合成示例，标注开发演示。
- 博客保留实验条件与失败边界；浏览器缓存演示仅解析字符串，不调用模型，也不提供性能数字。
- 原有私人试学课程未复制到这个公开网站。
- 关于页和简历沿用原站已公开资料；这次没有新增电话或外部追踪服务。

## 发布检查

```powershell
python -X utf8 scripts/build_site.py --check
python -X utf8 scripts/check_site.py
python -X utf8 -m unittest discover -s tests -v
node --check assets/site.js
```

浏览器还需检查桌面和手机、菜单、博客筛选与空结果、复制代码、缓存实验的更新/改名/重置。页面源码检查不替代浏览器验证。
