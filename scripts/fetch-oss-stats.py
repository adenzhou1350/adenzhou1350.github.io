#!/usr/bin/env python3
"""
抓取 GitHub 公开数据，写成 oss-stats.json 供站点读取。

设计原则：任何一步失败都不能让站点挂掉——
脚本失败则 JSON 不更新，页面继续用上一次的值（含内置兜底）。
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER = "adenzhou1350"
API = "https://api.github.com"
TOKEN = os.environ.get("GH_TOKEN", "")
OUT = "oss-stats.json"

# 上游项目白名单：只统计真正合入的代码仓库（排除自己 fork 的仓库与清单类仓库）
UPSTREAM = {
    "vllm-project/vllm",
    "kvcache-ai/Mooncake",
    "InternLM/lmdeploy",
    "fla-org/flash-linear-attention",
    "mlc-ai/TIRx-harness",
}
OWN = f"{USER}/kernel_opt_agent"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "aden-site-oss-stats",
    **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
}


def search_url(q, **params):
    # 注意：不能用 urlencode，它会把查询串里的空格编成 '+'，
    # GitHub 搜索接口要求 %20。冒号必须保留原样，否则语法不成立。
    parts = ["q=" + urllib.parse.quote(q, safe=":")]
    for k, v in params.items():
        parts.append(f"{k}={v}")
    return API + "/search/issues?" + "&".join(parts)


def get_search(q, **params):
    req = urllib.request.Request(search_url(q, **params), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path):
    req = urllib.request.Request(API + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def search_total(q):
    return get_search(q, per_page=1)["total_count"]


def search_all(q):
    out, page = [], 1
    while True:
        items = get_search(q, per_page=100, page=page)["items"]
        out += items
        if len(items) < 100 or len(out) >= 500:
            break
        page += 1
    return out


def repo_of(item):
    return item["repository_url"].split("/repos/")[-1]


def main():
    merged_q = f"author:{USER} is:pr is:merged"
    merged = search_all(merged_q)

    by_repo = {}
    for it in merged:
        by_repo[repo_of(it)] = by_repo.get(repo_of(it), 0) + 1

    upstream = sorted(
        ({"repo": r, "count": c} for r, c in by_repo.items() if r in UPSTREAM),
        key=lambda x: -x["count"],
    )
    # 白名单里有但这次没返回的（理论上不该发生），补零保证页面不缺项
    got = {u["repo"] for u in upstream}
    for r in sorted(UPSTREAM - got):
        upstream.append({"repo": r, "count": 0})

    open_total = search_total(f"author:{USER} is:pr is:open")
    reviewed_total = search_total(f"reviewed-by:{USER} type:pr")
    open_repos = len({repo_of(i) for i in
                      search_all(f"author:{USER} is:pr is:open")})

    profile = get(f"/users/{USER}")
    data = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "mergedTotal": len(merged),
        "upstreamMerged": sum(u["count"] for u in upstream),
        "upstreamRepos": [u["repo"] for u in upstream if u["count"] > 0],
        "upstreamBreakdown": upstream,
        "ownRepo": {"repo": OWN, "merged": by_repo.get(OWN, 0)},
        "openTotal": open_total,
        "openRepoCount": open_repos,
        "reviewedTotal": reviewed_total,
        "publicRepos": profile.get("public_repos", 0),
        "followers": profile.get("followers", 0),
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"✓ merged={data['mergedTotal']} upstream={data['upstreamMerged']} "
          f"({len(data['upstreamRepos'])} repos) reviewed={data['reviewedTotal']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print(f"✗ 抓取失败，保留上一次的 oss-stats.json：{e}", file=sys.stderr)
        sys.exit(1)
