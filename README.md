# Aden / 周栩丞 · 个人网站

AI Infra 与具身 Agent 的作品集、博客和教学空间。

线上入口：https://adenzhou1350.github.io/

首页按「个人介绍 → 开源贡献 → Bonsai / Jev 两个主要项目 → 工程笔记与浏览器练习 → 联系」组织。贡献区保留紧凑的项目入口，并选三条近期改动直达具体 PR；完整改动说明留在贡献页。教学入口保留在导航、项目导读和练习区。Bonsai 配图是三值编码示意，Jev 使用完整实验截图，不裁掉评测说明。

- `/projects/`：Jev 决策模型实战、Bonsai 低比特教学、模型实验、Agent 工具与 fork 扩展。
- `/blog/`：技术复盘，支持分类和关键词筛选。
- `/learn/`：Jev 决策模型、Bonsai 低比特专题和浏览器交互实验。Bonsai 主按钮直达三值编码实验，旁边保留完整导读与仓库入口。
- `/learn/fsspec-relative-path/`：文件名与列表的路径练习。浏览器比较六种预设流程，下载包重跑公开修复前后的真实文件传输；首页练习入口直达 `#path-demo`。
- `/learn/jev-decision-model/`：从随附的 CPU 推箱子策略进入候选打分、训练和页面按钮选择。
- `/learn/bonsai-low-bit/`：先在浏览器里操作三值打包并复制当前 Python 示例，再进入 CPU / QAT 教学与 27B、35B、122B 单卡部署。`#ternary-demo` 可直接打开编码实验。
- `/contributions/`：参与贡献的开源项目。首页展示 6 个重点项目，完整页列出已核对的 22 个项目；点击卡片，直接查看本人在对应仓库已合并的 PR。近期改动直链 TileLang、Agent Retrieval Bench、DeepSpeed 的具体修复，日期按北京时间显示。
- `/about/`：公开职业经历、教育、TileLang 修复与 5090 量化案例入口。首页联系区和关于页显示现有公开邮箱，方便没有默认邮件客户端的读者直接复制。
- `/contributions/stories/`：PR 背后的修复过程。先展示文章，再展开 2026-10-28 核对的 90 条公开合并记录，支持关键词、项目和“已有复盘”筛选；项目卡片仍直接打开 GitHub。

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

教学内容把命令中的 `blog` 换成 `learn`。同名内容不会被覆盖。已发布文章撤回时，设置 `draft: true`、`withdrawn: true` 和 `withdrawal_reason`。构建会用标记为 `noindex` 的撤回说明替换旧正文，并从目录、RSS 和站点地图中移除入口；原始 Markdown 仍然保留。只设置 `draft` 不会自动清理旧生成页。

当前内容目录：

| 栏目 | 文章 / 专题 | 源文件 |
|---|---|---|
| 博客 | TileLang：返回 False 之前，字典已经被改了 | `content/posts/tilelang-descriptor-map.md` |
| 博客 | 一个标量参数，为什么让 DeepSpeed 初始化失败？ | `content/posts/deepspeed-scalar-byte-view.md` |
| 博客 | 空列表能建表，换成迭代器却报错 | `content/posts/lancedb-empty-iterable.md` |
| 博客 | 换了推理后端，为什么旧测试还不能丢？ | `content/posts/sglang-renderer-regression.md` |
| 博客 | Agent 没读到的内容，不该影响检索结果 | `content/posts/agent-retrieval-read-budget.md` |
| 博客 | 单张 5090 跑 122B MoE：显存、分数和没用上的优化 | `content/posts/bonsai-5090-experiment.md` |
| 博客 | TileLang 同步修复：一个 block 报到了两次 | `content/posts/tilelang-grid-barrier.md` |
| 博客 | 截图更新了，为什么评分还是旧的？ | `content/posts/image-cache-identity.md` |
| 博客 | ptxas 解析器混读了两份 kernel 报告 | `content/posts/kernel-report-boundaries.md` |
| 交互教程 | 同一个文件名，套进列表就下载失败了 | `content/learn/fsspec-relative-path.md` |
| 教学专题 | Jev 决策模型：从推箱子学候选打分 | `content/learn/jev-decision-model.md` |
| 教学专题 | Bonsai 量化入门：三值编码、QAT 和单卡推理 | `content/learn/bonsai-low-bit.md` |
| 交互教程 | 文件名没变，缓存为什么会返回旧结果？ | `content/learn/cache-identity.md` |

Nest 于 2026-10-10 暂停更新：网站推荐和教学入口已撤下，旧教程地址仅显示暂停说明。`content/learn/nest-first-workflow.md`、演示图片、仓库和历史代码保留，不作为当前项目推广。

Bonsai 在目录中设置 `featured: true`，由教学页的专题组件呈现；实验状态以公开仓库为准。项目页计数按 `content/projects.json` 的实际条目生成。

```powershell
python -X utf8 scripts/build_site.py
python -X utf8 scripts/check_site.py
git diff --check
```

现有 GitHub Pages 从已提交的静态文件发布；只改 Markdown 而不重建不会更新正文。推送到网站的发布分支后，以线上页面实际内容确认完成。

## 文案约定

PR 复盘在 `content/catalog.json` 中增加 `contribution_prs` 数组，填写 `content/contributor-projects.json` 已核对的完整 PR URL。发布的文章会自动进入修复记录页，草稿不进入；不在快照中的 PR 会使构建失败，需先核对贡献归属与合并状态。一个案例可关联多条后续修复，但正文应说明各条的作用。原问题由其他人报告时保留署名；无法从历史材料确认的定位过程不要编写。每篇优先写触发输入、调用链、原因、修复取舍和验证边界；简单改动可以只留原始链接，不必凑成长文。

首批 7 篇记录对应 10 条 PR，其中 Agent 检索文章主体是 #4/#6，#13/#16 是后续补充。SGLang renderer 的独立复现不是本人已合并 PR，不列入该关联。TileLang #3484 的三项回归在最终评审中被移除，文章明确区分历史验证与最终文件；DeepSpeed #8642 只引用 CPU/Gloo 验证；LanceDB #4538 的 268 项通过仅限两个测试模块。此次写作未重新执行这些历史实验。

项目先说用途和当前能做什么，文章直接写遇到的问题。栏目标题用内容名称，少用口号、排比和抽象总结。可以用第一人称，但不要编造经历、客户或成果。

编辑时保留代码、链接、实验数字和使用限制。AI 辅助整理的说明照常保留。2026-10-10 的文案修订参考了 [Humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md)，按段落重写后再检查事实是否变化。

## 支持的正文格式

- `##`、`###` 标题；一级标题由目录元数据提供。
- 普通段落、非嵌套有序或无序列表、链接、粗体与行内代码。
- 带语言名的三反引号代码块、引用块和简单 Markdown 表格。
- 独占一行的图片：`![图片说明](/assets/images/example.jpg)`。先把图片放入 `assets/images/`；说明同时用作替代文本和图注。暂不支持外链图片。
- `{{CACHE_DEMO}}` 是本站缓存教学实验的专用组件标记。
- `{{TERNARY_DEMO}}` 是 Bonsai 导读的三值编码组件：五个原生选项、当前展开式、打包整数、8 位二进制、解包结果和往返反馈。Python 示例随当前输入更新，可复制；关闭 JavaScript 时保留默认示例，修改选项禁用。
- `{{PATH_DEMO}}` 从 `content/components/path-demo.html` 载入路径教学组件。六个固定组合只演示 Windows `C:/lesson` 下的分支和父目录；不执行下载。此教程单独加载 `assets/path-demo.css` 和 `assets/path-demo.js`，不增加其他页面的脚本。

HTML 源码会被转义，正文不运行任意 HTML 或 JavaScript。复制代码需要浏览器允许剪贴板写入；失败时仍可手动选择代码。

## 文件结构

```text
content/catalog.json          文章和教程目录
content/posts/*.md            博客正文
content/learn/*.md            教学正文
content/projects.json         项目事实、边界与链接
content/contributor-projects.json  贡献项目、核对日期与原始 PR 证据
content/contributions.json    旧精选案例存档（不参与页面生成）
scripts/build_site.py         模板与静态内容生成
scripts/new_content.py        新建草稿
scripts/check_site.py         链接、锚点、元数据和内容边界检查
assets/site.css               当前设计与响应式布局
assets/site.js                菜单、筛选、复制、教学交互
assets/images/                已公开项目的开发演示图片
```

`index.html`、各栏目及内容目录、`details.html`、`feed.xml`、`sitemap.xml` 由构建生成；不要把新文章只写进生成文件。

## 内容来源与范围

- 项目依据对应公开仓库。Bonsai 标注公开教学与实验记录，minimind-diffusion 标注学习实验，kernel_opt_agent 标注 fork 扩展。
- Bonsai 导读核对至 2026-10-21：三款权重已公开。35B 历史固定步数热解码 59.33 / 49.85、122B 历史短请求 CLI 21.72–24.00、27B 公开路径 9.37 token/s，测试口径不同；27B 私有 Graph 13.02 仅为实验结论，便携 GPU 未验证，不发布。本轮优化已停止。保留 R35-8192 与未完成全专家 QAT 的区别、便携入口验证范围及质量限制，历史博客只补当前部署入口。
- Bonsai 编码小实验的随附 Python 示例只使用标准功能。仓库 CPU 检查点测试使用 POSIX 目录同步，教程按 Linux CPU 路线说明；没有宣称 Windows 原生支持或完整 122B 一键复刻。
- 三值编码交互只在浏览器本地计算，不调用模型或估算显存。反馈链接打开现有公开邮箱，预填文章链接与当前输入，由读者自行检查发送；没有自动收集、上传或新增后台。
- 贡献项目名单于 2026-10-28 按 GitHub 公开搜索与 PR API 核对，共 22 个仓库、90 条已合并 PR；各条原始链接和合并时间保存在 `content/contributor-projects.json`。Contributor 表示有公开合并贡献，不表示维护者或核心成员身份。项目卡片限定 `author:adenzhou1350`、`is:pr`、`is:public`、`is:merged` 和对应的 `repo:`，打开实时结果；全量入口排除本人名下仓库。页面展示的项目数是核对日快照；修复记录索引的 PR 总数也明确标注核对日期，不代表实时数量。`recent` 是人工选择的三条近期改动，并非全量动态；只从已核对的公开合并记录中选择。新增项目或更换近期改动时核对合并证据、更新日期并重建；已有项目后续合并的 PR 会自动出现在 GitHub 查询中。`contributions.json` 和 `oss-stats.json` 仅保留为历史数据。
- Jev 导读依据公开仓库 `3a55d60` 的三节课、安装说明与实验记录。推箱子为独立 CNN；页面按钮使用冻结的 Qwen3.5-0.8B 与共享打分头，保留模型快照、合成数据和评测范围。随附页面 head 的原始底座 revision 未公开，默认下载后按训练个人 head 的路线操作，匹配文件指纹的快照可走随附 head 路线。演示截图取自该仓库 `docs/assets/demo-sokoban.jpg`，按项目 MIT 许可使用；不是本站在线模型服务。
- 保留的 Nest 历史图片取自其公开仓库 `docs/assets/overview.jpg`，使用合成示例；目前不在公开页面展示。
- 博客保留实验条件与失败边界；浏览器缓存演示仅解析字符串，不调用模型，也不提供性能数字。
- 2026-10-13 发布的 TileLang 案例依据已合并 PR #3400 的历史测试；Bonsai 案例依据公开提交 `01c01ff8a913bf03cf8af7c659984af445f79f93`，区分 122B 文本路径与 35B R35-8192 的显存口径，保留质量门槛与复现范围。写作时未重跑 GPU 实验。首页自动展示最新两篇，Bonsai 导读与实测案例互链。
- 2026-10-13 补充三个公开仓库的使用与证据入口：Bonsai 的标准库检查只校验公开文件和摘要算术；kernel_opt_agent 入口区分已试跑的轻量快照与仅核对源码的集成分支；minimind-diffusion 的出处页区分不同规模、不同训练阶段的历史观察。网站没有把这些整理写成新的性能结果。
- 原有私人试学课程未复制到这个公开网站。
- 关于页和简历沿用原站已公开资料；这次没有新增电话或外部追踪服务。
- 2026-10-28 的 Agent 检索案例依据公开已合并 PR #4/#6，补充 #13/#16。PR #6 的前后对照中，101 个公开样本的最终选择和非延迟指标不变；389/545 到 0/545 表示按项目正则计数的正文预算越界次数，不是供应商账单、模型准确率提升或本轮重跑结果。
- Bonsai 首页与项目卡直链现行部署指南；三款 Hugging Face 固定版本于 2026-10-28 核对可公开访问，未下载或重跑模型。文章元数据显示原发布日和实际内容更新日，入口核对不改写实验日期。
- 2026-10-29 的 SGLang 复现笔记依据 10 月 26 日固定版本的 CPU 原生组件实验。原问题由 05yuki 报告，旧语义断言来自上游；8 个现有 renderer 方法在披露过适配的环境中通过，不代表完整 CI。随附 JSON 是不含私有路径和原始对话的历史结果摘录，不是完整复现包；没有重跑最新版本、验证修复或测量模型质量。
- fsspec 路径教程对应公开已合入 PR #2376。浏览器模拟的六个组合与 Python `ntpath` 对照，显示源、目标同时采用标量或列表；实际 HTTP 回放为前版两项预期失败加六项成功、修复版八项成功，后者逐项核对完整文件字节。下载包只含原创复现脚本、公开说明、脱敏结果和来源，不含 Scout、依赖源码缓存或原始日志。上游源码由脚本按固定提交下载并保留 BSD-3-Clause；没有新增软件许可。真实回放已于 10 月 29 日在 Windows Python 3.14.3 / aiohttp 3.13.5 验证，本次教程整理没有重复执行 HTTP 实验。

## 发布检查

```powershell
python -X utf8 scripts/build_site.py --check
python -X utf8 scripts/check_site.py
python -X utf8 -m unittest discover -s tests -v
node --check assets/site.js
node tests/test_ternary_demo.cjs
node tests/test_path_demo.cjs
node tests/test_pr_stories.cjs
```

`test_ternary_demo.cjs` 直接加载页面所用函数，穷举 243 种合法输入，检查编码唯一性、往返还原、默认值与两端值，并用 Python 实际执行全部 243 份当前输入代码。测试不另写一份编码器来代替页面实现。

`test_path_demo.cjs` 将页面使用的六种路径结果与 Python `ntpath` 对照，并通过记录型 `fs` 执行同一份 API 参数示例，检查两端同时切换列表、父目录、初始化和重置。它不冒充真实下载测试。

`test_pr_stories.cjs` 直接测试索引使用的筛选与事件处理，覆盖多词匹配、项目交叉条件、已有复盘、空结果、重置和脚本初始化。贡献关联测试拒绝未核对的 PR，并排除草稿。关闭 JavaScript 时完整索引仍在 HTML 中，筛选控件禁用。

浏览器还需检查桌面和手机、菜单、博客筛选与空结果、复制代码、缓存实验的更新/改名/重置，以及三值实验的键盘选择、重置、代码更新和邮件预填。页面源码检查不替代浏览器验证。
