#!/usr/bin/env python3
"""Collect and classify public Nowcoder interview experiences.

Conservative by design: public pages only, robots.txt on by default, low rate,
local cache, no login/CAPTCHA/private-content automation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path

UA = "big-tech-interviewer-skill/0.2 (public interview-experience research)"
DETAIL_HINTS = ("/discuss/", "/feed/main/detail/", "/community/", "/enterprise/")

ALIASES = {
    "companies": {
        "ByteDance": "字节 字节跳动 bytedance 抖音 飞书 火山引擎 tiktok",
        "Alibaba": "阿里 阿里巴巴 淘天 淘宝 天猫 蚂蚁 菜鸟 alibaba ant",
        "Tencent": "腾讯 微信 wxg ieg pcg teg csig tencent",
        "Meituan": "美团 大众点评 meituan",
        "JD": "京东 jd 京东物流",
        "Huawei": "华为 huawei od",
        "PDD": "拼多多 pdd temu",
        "Baidu": "百度 baidu",
        "Kuaishou": "快手 kuaishou",
        "Microsoft": "微软 microsoft",
        "Google": "谷歌 google",
        "Amazon": "亚马逊 amazon aws",
        "Meta": "meta facebook",
        "Apple": "苹果 apple",
    },
    "languages": {
        "Java": "java jvm spring springboot spring cloud mybatis",
        "C++": "c++ cpp stl 智能指针",
        "Python": "python django flask fastapi pandas",
        "Go": "golang go语言",
        "JavaScript/TypeScript": "javascript typescript react vue node",
        "C#": "c# .net",
        "Rust": "rust",
    },
    "roles": {
        "Backend": "后端 服务端 java开发 go开发 后台 server",
        "Frontend": "前端 web前端 react vue",
        "Algorithm/ML": "算法 机器学习 深度学习 推荐 nlp cv 大模型 llm",
        "Data": "数据开发 数据分析 数仓 大数据 etl bi",
        "Testing/QA": "测试 测开 qa 质量",
        "Client": "客户端 android ios 移动端",
        "Infra/SRE": "运维 sre 基础架构 云原生 devops",
        "Security": "安全 风控 攻防",
        "Product": "产品经理 pm 产品",
    },
}

ENTERPRISE = {
    "high_concurrency": "高并发 qps tps 峰值 流量突增 秒杀 抢购 热点",
    "consistency": "一致性 最终一致 强一致 分布式事务 事务 对账 补偿",
    "idempotency": "幂等 重复请求 重试 防重 去重 唯一键",
    "mq": "mq 消息队列 kafka rocketmq rabbitmq 消息堆积 顺序消息",
    "cache": "缓存 redis 缓存穿透 缓存击穿 缓存雪崩 热key bigkey",
    "database": "mysql 数据库 索引 慢查询 锁 死锁 分库分表 读写分离",
    "availability": "降级 熔断 限流 容灾 故障 宕机 可用性 slo sla",
    "observability": "监控 报警 日志 链路追踪 trace 指标 排查",
    "release": "灰度 发布 回滚 ab实验 feature flag",
    "security": "鉴权 权限 越权 风控 安全 加密 脱敏",
    "cost": "成本 资源 容量 扩容 压测 瓶颈",
    "order_payment": "订单 支付 库存 优惠券 购物车 退款 结算",
}

ROUND_PATTERNS = {
    "HR": r"\bhr\b|hr面|人事面|主管面",
    "一面": r"一面|1面|第一面|初面",
    "二面": r"二面|2面|第二面|复面",
    "三面": r"三面|3面|第三面|终面",
    "四面+": r"四面|五面|加面|交叉面|cto面",
}

SUPER_PATTERNS = [
    r"如果.*(宕机|崩|超时|失败|丢失|重复|乱序|不一致)",
    r"(10倍|十倍|百万|千万|亿级|峰值|突增|压测)",
    r"(线上|生产).*?(故障|事故|排查|回滚|止血)",
    r"(分布式事务|最终一致|对账|补偿|幂等|重复扣款|超卖)",
    r"(消息堆积|顺序消息|重复消费|消费失败)",
    r"(缓存雪崩|缓存击穿|缓存穿透|热key|bigkey)",
    r"(死锁|锁竞争|慢查询|索引失效|分库分表)",
    r"(降级|熔断|限流|容灾|多活|异地)",
]

QUESTION_MARKERS = ("?", "？", "怎么", "如何", "为什么", "讲一下", "说一下", "介绍一下", "设计", "排查")


class Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "div", "li", "br", "h1", "h2", "h3", "section"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.skip:
            self.skip -= 1
        if tag == "title":
            self.in_title = False
        if tag in {"p", "div", "li", "h1", "h2", "h3", "section"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip or not data.strip():
            return
        text = data.strip()
        if self.in_title:
            self.title += text
        self.parts += [text, " "]

    def text(self) -> str:
        raw = html.unescape("".join(self.parts))
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


@dataclass
class Classification:
    companies: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    rounds: list[str] = field(default_factory=list)
    enterprise_tags: list[str] = field(default_factory=list)
    project_question_count: int = 0
    super_hard_score: int = 0
    difficulty: str = "normal"


def norm_url(url: str, base: str | None = None) -> str | None:
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(base or "", url))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc.lower().endswith("nowcoder.com"):
        return None
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def fetch(url: str, cache: Path, ua: str, timeout: int) -> str:
    path = cache / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".html")
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
    path.write_text(text, encoding="utf-8")
    return text


def allowed(url: str, ua: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    robots = urllib.robotparser.RobotFileParser(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        robots.read()
        return robots.can_fetch(ua, url)
    except Exception:
        return False


def parse_html(page: str) -> tuple[str, str]:
    ex = Extractor()
    ex.feed(page)
    title = re.sub(r"[-_].*?牛客.*$", "", ex.title).strip() or "untitled"
    return title, ex.text()


def links(page_url: str, page: str) -> list[str]:
    out, seen = [], set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', page, flags=re.I):
        url = norm_url(href, page_url)
        if url and url not in seen and any(h in url for h in DETAIL_HINTS):
            seen.add(url)
            out.append(url)
    return out


def match_aliases(blob: str, table: dict[str, str]) -> list[str]:
    low = blob.lower()
    return [label for label, words in table.items() if any(w.lower() in low for w in words.split())]


def questions(text: str) -> list[str]:
    text = re.sub(r"([？?])", r"\1\n", text)
    text = re.sub(r"(?<!\d)[（(]?\d+[）).、]\s*", "\n", text)
    text = re.sub(r"(面试官问[:：]|问[:：]|追问[:：])", r"\n\1", text)
    found = []
    for chunk in re.split(r"[。；;\n]", text):
        q = re.sub(r"\s+", " ", chunk.strip(" -\t\n"))
        if 6 <= len(q) <= 260 and any(m in q for m in QUESTION_MARKERS):
            found.append(q)
    return list(dict.fromkeys(found))


def is_project(q: str) -> bool:
    low = q.lower()
    project_words = "项目 业务 系统 场景 线上 生产 架构 接口 服务 链路".split()
    return any(w in low for w in project_words) or any(w in low for ws in ENTERPRISE.values() for w in ws.split())


def classify(title: str, text: str, qs: list[str], pqs: list[str]) -> Classification:
    blob = f"{title}\n{text}"
    low = blob.lower()
    tags = [tag for tag, words in ENTERPRISE.items() if any(w.lower() in low for w in words.split())]
    score = sum(len(re.findall(p, "\n".join(pqs) or blob, flags=re.I)) for p in SUPER_PATTERNS) + min(len(tags), 6)
    if any("项目" in q and ("如果" in q or "线上" in q or "故障" in q) for q in pqs):
        score += 3
    return Classification(
        companies=match_aliases(blob, ALIASES["companies"]),
        languages=match_aliases(blob, ALIASES["languages"]),
        roles=match_aliases(blob, ALIASES["roles"]),
        rounds=[k for k, p in ROUND_PATTERNS.items() if re.search(p, blob, flags=re.I)],
        enterprise_tags=tags,
        project_question_count=len(pqs),
        super_hard_score=score,
        difficulty="super_hard" if score >= 8 or len(pqs) >= 8 else "hard" if score >= 4 or len(pqs) >= 4 else "normal",
    )


def collect(seed_urls: list[str], args) -> list[str]:
    queue = [u for u in (norm_url(u) for u in seed_urls) if u]
    seen, detail = set(), []
    while queue and len(seen) < args.max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if args.respect_robots and not allowed(url, args.user_agent):
            print(f"[skip robots] {url}", file=sys.stderr)
            continue
        try:
            page = fetch(url, args.cache_dir, args.user_agent, args.timeout)
        except Exception as exc:
            print(f"[fetch failed] {url}: {exc}", file=sys.stderr)
            continue
        if any(h in url for h in DETAIL_HINTS):
            detail.append(url)
        for link in links(url, page):
            if link not in seen and len(queue) < args.max_pages * 4:
                queue.append(link)
        time.sleep(args.delay + random.random() * args.delay * 0.35)
    return detail[: args.max_pages]


def read_url_file(path: Path | None) -> list[str]:
    if not path:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def write_outputs(records: list[dict], out: Path) -> None:
    (out / "records.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    with (out / "summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fields = "difficulty super_hard_score company role language round enterprise_tags project_question_count title url".split()
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for r in records:
            c = r["classification"]
            writer.writerow({
                "difficulty": c["difficulty"],
                "super_hard_score": c["super_hard_score"],
                "company": "|".join(c["companies"]),
                "role": "|".join(c["roles"]),
                "language": "|".join(c["languages"]),
                "round": "|".join(c["rounds"]),
                "enterprise_tags": "|".join(c["enterprise_tags"]),
                "project_question_count": c["project_question_count"],
                "title": r["title"],
                "url": r["url"],
            })
    lines = ["# Nowcoder Project-Grilling Bank", "", "Keep source URLs. Distill patterns before publishing.", ""]
    for r in records:
        if not r["project_questions"]:
            continue
        c = r["classification"]
        lines += [f"## {c['difficulty']} | {','.join(c['companies']) or 'Unknown'} | {','.join(c['roles']) or 'Unknown'} | {','.join(c['languages']) or 'Unknown'}", "", f"Source: {r['url']}", ""]
        lines += [f"- {q}" for q in r["project_questions"]] + [""]
    (out / "project_grilling_bank.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Collect public Nowcoder interview experiences and classify project-grilling signal.")
    p.add_argument("--seed-url", action="append", default=[])
    p.add_argument("--url-file", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("data/nowcoder"))
    p.add_argument("--max-pages", type=int, default=30)
    p.add_argument("--delay", type=float, default=3.0)
    p.add_argument("--timeout", type=int, default=20)
    p.add_argument("--user-agent", default=UA)
    p.add_argument("--respect-robots", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--save-full-text", action="store_true")
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir = args.out_dir / ".cache"
    args.cache_dir.mkdir(exist_ok=True)
    seeds = args.seed_url + read_url_file(args.url_file)
    if not seeds:
        print("Provide --seed-url or --url-file.", file=sys.stderr)
        return 2
    urls = collect(seeds, args)
    if not urls:
        print("No candidate detail URLs found. Try direct public detail URLs.", file=sys.stderr)
        return 1
    records = []
    for url in urls:
        title, text = parse_html(fetch(url, args.cache_dir, args.user_agent, args.timeout))
        qs = questions(text)
        pqs = [q for q in qs if is_project(q)]
        c = classify(title, text, qs, pqs)
        records.append({
            "url": url,
            "title": title,
            "text_excerpt": text if args.save_full_text else text[:3000],
            "questions": qs[:80],
            "project_questions": pqs[:80],
            "classification": asdict(c),
        })
    write_outputs(records, args.out_dir)
    counts: dict[str, int] = {}
    for r in records:
        d = r["classification"]["difficulty"]
        counts[d] = counts.get(d, 0) + 1
    print(json.dumps({"records": len(records), "difficulty_counts": counts, "out_dir": str(args.out_dir)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
