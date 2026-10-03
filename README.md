# 周栩丞 · 个人站

单页静态站点。零依赖、零构建、没有 npm，纯 HTML + CSS + JS，推上 GitHub 就能直接跑。

## 目录结构

```
index.html                              整个页面
assets/
  styles.css                            全部样式
  main.js                               淡入上移 + 滚动进度线 + 顶栏收拢
  art/stack-layers.svg                  分层示意图
  files/aden-zhou-xucheng-cv.pdf        简历原件
```

改内容只需要动 `index.html`，改样式只需要动 `assets/styles.css`。没有构建步骤，改完 push 就生效。

---

## 一、发布到 GitHub Pages

### 1. 建仓库

在 GitHub 新建仓库，**仓库名必须是 `adenzhou1350.github.io`**。

这个名字很关键 —— 填对之后网址就是 `https://adenzhou1350.github.io`，不需要买任何域名。这是 GitHub 为每个用户免费提供的。

- 不要勾选 "Add a README file"
- 选 Public

### 2. 推送文件

在 `aden-github-pages` 目录下执行：

```bash
git init
git add .
git commit -m "个人站上线"
git branch -M main
git remote add origin https://github.com/adenzhou1350/adenzhou1350.github.io.git
git push -u origin main
```

### 3. 打开 Pages

仓库页面 → **Settings** → 左侧 **Pages** → Build and deployment：

- Source 选 `Deploy from a branch`
- Branch 选 `main`，目录选 `/ (root)`
- 保存

等 1 分钟左右，`https://adenzhou1350.github.io` 就能访问。

---

## 二、以后绑定自己的域名

现在这个 `adenzhou1350.github.io` 已经够用了。如果以后想要 `adenzhou.me` 这种更短的：

**1. 买域名。** `.dev` / `.me` / `.site` 首年通常几十到一百多块，Namecheap、Cloudflare Registrar、阿里云都行。

**2. 加 DNS 记录。** 在域名的 DNS 面板加一条 CNAME：

| 类型 | 主机 | 指向 |
|---|---|---|
| CNAME | `@` | `adenzhou1350.github.io` |

**3. 提交 CNAME 文件。** 把本目录的 `CNAME.example` 复制一份改名为 `CNAME`（无扩展名），内容改成你的域名，**不要带 `https://`**：

```
adenzhou.me
```

```bash
git add CNAME
git commit -m "绑定自定义域名"
git push
```

**4. 等证书。** Settings → Pages 里的 Custom domain 会自动变成你的域名，GitHub 会自动签发 HTTPS 证书，通常几分钟到一天。

---

## 三、需要注意的

**简历 PDF 是公开的。** `assets/files/aden-zhou-xucheng-cv.pdf` 含完整个人信息（姓名、邮箱、电话、教育、工作经历），仓库是公开的话，任何人都能 clone 下来。这和当前已发布站点的状态一致，但要注意 GitHub 仓库比静态托管更容易被搜索引擎和第三方镜像抓取。

如果不希望 PDF 随仓库公开，两个选择：

- 把 PDF 换成图床链接，从页面里去掉本地文件
- 或者把仓库设为 Private（但 GitHub Pages 对 Private 仓库需要 GitHub Pro）

**力扣主页链接待确认。** `index.html` 里那个 `leetcode.cn/u/...` 地址是从旧记录还原的，leetcode.cn 对任何 slug 都返回 200，无法自动验证它是否有效。发布前请自己点开确认一次，在 `index.html` 的两处（首屏 quicklinks 和页脚 foot-links）都要改。

**站内链接用的是相对路径。** 所以这个目录可以整体搬到任何静态托管上，不需要改代码。
