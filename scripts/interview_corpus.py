#!/usr/bin/env python3
"""Build a classified interview-experience corpus and project-grilling model.

Inputs:
- public URLs from Nowcoder/Xiaohongshu/generic pages when robots.txt allows
- raw .txt/.md/.html files exported manually from any platform
- CSV files with source,title,url,text and optional company/language/role/project

The script does not automate login, CAPTCHA, private feeds, or access-control
bypass. It stores excerpts by default and distills patterns before publication.
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
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path

UA = "big-tech-interviewer-skill/0.3 (public interview-experience research)"

SOURCE_HOSTS = {
    "nowcoder": ("nowcoder.com",),
    "xiaohongshu": ("xiaohongshu.com", "xhslink.com"),
    "generic": (),
}

DETAIL_HINTS = {
    "nowcoder": ("/discuss/", "/feed/main/detail/", "/community/", "/enterprise/"),
    "xiaohongshu": ("/explore/", "/discovery/item/", "/search_result/"),
    "generic": ("/",),
}

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
        "Xiaomi": "小米 xiaomi",
        "NetEase": "网易 netease",
        "Bilibili": "哔哩 b站 bilibili",
        "Microsoft": "微软 microsoft",
        "Google": "谷歌 google",
        "Amazon": "亚马逊 amazon aws",
        "Meta": "meta facebook",
        "Apple": "苹果 apple",
    },
    "languages": {
        "Java": "java jvm spring springboot springcloud mybatis",
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
    "release": "灰度 发布 回滚 ab实验 featureflag feature_flag",
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

QUESTION_MARKERS = ("?", "？", "怎么", "如何", "为什么", "什么", "吗", "讲一下", "说一下", "介绍一下", "场景题", "系统设计", "项目相关")
PROJECT_CONTEXT = "项目 业务 系统 线上 生产 架构 接口 服务 链路 高并发 高性能 部署 协作 发布 故障 事故 止血 回滚 排查 热点 分片 分布式 微服务".split()
TEXTBOOK_STARTERS = ("什么是", "说一下", "讲一下", "介绍一下", "了解", "谈谈")
NOISE_MARKERS = (
    "包装简历", "哈哈", "牛客上", "专栏", "前传", "http://", "https://", "未填写", "招聘", "加班",
    "base", "道心破碎", "人生开挂", "非常开心", "凌晨改", "小bug", "慢慢能", "以下是具体",
    "项目链接", "网盘", "面试官自己提取", "盆友", "单身：", "看完",
)
TEXTBOOK_PATTERNS = (r"是什么", r"有哪些", r"原理", r"区别", r"优缺点", r"适用场景")

DRILL_TEMPLATES = {
    "high_concurrency": "如果峰值流量突然扩大 10 倍，你这个项目最先崩在哪里？怎么压测、限流、扩容、回退？",
    "consistency": "如果核心链路部分成功、部分失败，你如何保证最终一致？补偿、对账、人工兜底分别怎么设计？",
    "idempotency": "如果用户重复点击、网关重试、MQ 重复消费同时发生，你的幂等键、状态机和唯一约束怎么配合？",
    "mq": "如果消息积压、乱序、重复消费、消费失败同时出现，你怎么定位、止血、恢复数据？",
    "cache": "如果 Redis 热 key 或缓存击穿把 DB 打满，你怎么发现、隔离、降级、预热？",
    "database": "如果线上慢查询和锁竞争导致 P99 飙升，你怎么从索引、事务、隔离级别、分库分表上拆？",
    "availability": "如果依赖服务 30% 超时，你的熔断、降级、重试、超时预算和用户体验怎么取舍？",
    "observability": "如果线上已经出事，你有哪些指标、日志、trace 能在 10 分钟内定位根因？",
    "release": "如果灰度后指标轻微劣化但业务催上线，你怎么判断继续、回滚还是扩大灰度？",
    "security": "如果出现越权、刷单、重复退款或敏感信息泄露，你在接口、数据和审计层怎么补？",
    "cost": "如果老板要求成本降 30% 但 SLA 不变，你会从容量、缓存、存储、异步化哪里下手？",
    "order_payment": "如果订单、支付、库存、优惠券任一环节状态不一致，你怎么设计状态机和恢复任务？",
}


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
        if self.in_title:
            self.title += data.strip()
        self.parts += [data.strip(), " "]

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
    projects: list[str] = field(default_factory=list)
    enterprise_tags: list[str] = field(default_factory=list)
    project_question_count: int = 0
    super_hard_score: int = 0
    difficulty: str = "normal"


def infer_source(url: str, default: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if "nowcoder.com" in host:
        return "nowcoder"
    if "xiaohongshu.com" in host or "xhslink.com" in host:
        return "xiaohongshu"
    return default


def infer_source_from_text(name: str, text: str, default: str) -> str:
    blob = f"{name}\n{text}".lower()
    if "nowcoder" in blob or "牛客" in blob:
        return "nowcoder"
    if "xiaohongshu" in blob or "小红书" in blob or "xhs" in blob:
        return "xiaohongshu"
    return default


def norm_url(url: str, source: str, base: str | None = None) -> str | None:
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(base or "", url))
    if parsed.scheme not in {"http", "https"}:
        return None
    hosts = SOURCE_HOSTS.get(source, ())
    if hosts and not any(parsed.netloc.lower().endswith(h) for h in hosts):
        return None
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def robots_allowed(url: str, ua: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    robots = urllib.robotparser.RobotFileParser(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        robots.read()
        return robots.can_fetch(ua, url)
    except Exception:
        return False


def fetch(url: str, cache: Path, ua: str, timeout: int) -> str:
    path = cache / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".html")
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
    path.write_text(text, encoding="utf-8")
    return text


def parse_html(page: str) -> tuple[str, str]:
    ex = Extractor()
    ex.feed(page)
    title = re.sub(r"[-_].*?(牛客|小红书).*$", "", ex.title).strip() or "untitled"
    return title, ex.text()


def discover_links(page_url: str, page: str, source: str) -> list[str]:
    hints = DETAIL_HINTS.get(source, DETAIL_HINTS["generic"])
    out, seen = [], set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', page, flags=re.I):
        url = norm_url(href, source, page_url)
        if url and url not in seen and any(h in url for h in hints):
            seen.add(url)
            out.append(url)
    return out


def match_aliases(blob: str, table: dict[str, str], hints: str = "") -> list[str]:
    low = f"{hints}\n{blob}".lower()
    return [label for label, words in table.items() if any(w.lower() in low for w in words.split())]


def merge_hint(hint: str, inferred: list[str]) -> list[str]:
    return list(dict.fromkeys([x for x in [hint] + inferred if x]))


def split_questions(text: str) -> list[str]:
    text = re.sub(r"([？?])", r"\1\n", text)
    text = re.sub(r"(?<!\d)[（(]?\d+[）).、]\s*", "\n", text)
    text = re.sub(r"(面试官问[:：]|问[:：]|追问[:：])", r"\n\1", text)
    found = []
    for chunk in re.split(r"[。；;\n]", text):
        q = re.sub(r"\s+", " ", chunk.strip(" -\t\n"))
        if 6 <= len(q) <= 260 and looks_like_question(q) and not is_noise(q):
            found.append(q)
    return list(dict.fromkeys(found))


def looks_like_question(q: str) -> bool:
    if any(m in q for m in QUESTION_MARKERS):
        return True
    if re.search(r"(设计一个|如何设计|怎么设计|怎么排查|如何排查|如果.*怎么|场景[:：])", q):
        return True
    return False


def is_noise(q: str) -> bool:
    return any(mark.lower() in q.lower() for mark in NOISE_MARKERS)


def is_textbook_question(q: str) -> bool:
    strong_project = any(w in q for w in ["项目", "系统", "线上", "生产故障", "场景题", "高并发", "业务链路", "服务发布"])
    return not strong_project and any(re.search(p, q) for p in TEXTBOOK_PATTERNS)


def extract_projects(blob: str, hint: str = "") -> list[str]:
    found = []
    for pattern in [r"项目(?:是|为|叫|：|:)\s*([^，。；;\n]{2,24})", r"做过([^，。；;\n]{2,24})项目"]:
        found += [m.strip() for m in re.findall(pattern, blob)]
    if hint:
        found = [hint] + found
    clean = []
    for item in found:
        if any(mark in item for mark in QUESTION_MARKERS) or any(bad in item for bad in ["面试官", "包装简历", "看看吗"]):
            continue
        clean.append(item)
    return list(dict.fromkeys(clean))[:5]


def is_project_question(q: str) -> bool:
    low = q.lower()
    has_context = any(w in low for w in PROJECT_CONTEXT)
    has_enterprise = any(w in low for ws in ENTERPRISE.values() for w in ws.split())
    has_failure = any(w in low for w in "如果 超时 失败 丢失 重复 乱序 不一致 崩溃 宕机 堆积 击穿 雪崩 死锁 慢查询 限流 降级 熔断 补偿 对账".split())
    is_textbook = q.startswith(TEXTBOOK_STARTERS) and not has_failure and "项目" not in q and "系统" not in q
    if is_noise(q) or is_textbook_question(q):
        return False
    return looks_like_question(q) and ((has_context and not is_textbook) or (has_enterprise and has_failure))


def classify(title: str, text: str, qs: list[str], pqs: list[str], hints: dict[str, str]) -> Classification:
    blob = f"{title}\n{text}"
    title_blob = title
    low = blob.lower()
    tags = [tag for tag, words in ENTERPRISE.items() if any(w.lower() in low for w in words.split())]
    score = sum(len(re.findall(p, "\n".join(pqs) or blob, flags=re.I)) for p in SUPER_PATTERNS) + min(len(tags), 6)
    if any("项目" in q and ("如果" in q or "线上" in q or "故障" in q) for q in pqs):
        score += 3
    return Classification(
        companies=merge_hint(hints.get("company", ""), match_aliases(title_blob, ALIASES["companies"]) or match_aliases(blob[:1200], ALIASES["companies"])),
        languages=merge_hint(hints.get("language", ""), match_aliases(title_blob, ALIASES["languages"]) or match_aliases(blob[:1200], ALIASES["languages"])),
        roles=merge_hint(hints.get("role", ""), match_aliases(title_blob, ALIASES["roles"]) or match_aliases(blob[:1200], ALIASES["roles"])),
        rounds=[k for k, p in ROUND_PATTERNS.items() if re.search(p, blob, flags=re.I)],
        projects=extract_projects(blob, hints.get("project", "")),
        enterprise_tags=tags,
        project_question_count=len(pqs),
        super_hard_score=score,
        difficulty="super_hard" if score >= 8 or len(pqs) >= 8 else "hard" if score >= 4 or len(pqs) >= 4 else "normal",
    )


def read_url_file(path: Path | None) -> list[str]:
    if not path:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def collect_urls(seeds: list[str], args) -> list[dict]:
    queue = [(infer_source(u, args.source), u) for u in seeds]
    seen, raw = set(), []
    while queue and len(seen) < args.max_pages:
        source, url = queue.pop(0)
        url = norm_url(url, source)
        if not url or url in seen:
            continue
        seen.add(url)
        if args.respect_robots and not robots_allowed(url, args.user_agent):
            print(f"[skip robots] {url}", file=sys.stderr)
            continue
        try:
            page = fetch(url, args.cache_dir, args.user_agent, args.timeout)
        except Exception as exc:
            print(f"[fetch failed] {url}: {exc}", file=sys.stderr)
            continue
        title, text = parse_html(page)
        raw.append({"source": source, "url": url, "title": title, "text": text, "hints": {}})
        for link in discover_links(url, page, source):
            if link not in seen and len(queue) < args.max_pages * 4:
                queue.append((source, link))
        time.sleep(args.delay + random.random() * args.delay * 0.35)
    return raw[: args.max_pages]


def load_raw_dir(path: Path | None, source: str) -> list[dict]:
    if not path:
        return []
    rows = []
    for file in sorted(path.rglob("*")):
        if file.suffix.lower() not in {".txt", ".md", ".html", ".htm"}:
            continue
        text = file.read_text(encoding="utf-8", errors="replace")
        title, body = parse_html(text) if file.suffix.lower() in {".html", ".htm"} else (file.stem, text)
        row_source = infer_source_from_text(str(file), body, source)
        rows.append({"source": row_source, "url": f"file:{file.name}", "title": title, "text": body, "hints": {}})
    return rows


def load_csv(path: Path | None, default_source: str) -> list[dict]:
    if not path:
        return []
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            text = row.get("text") or row.get("content") or row.get("正文") or ""
            title = row.get("title") or row.get("标题") or "untitled"
            source = row.get("source") or row.get("来源") or default_source
            url = row.get("url") or row.get("链接") or ""
            hints = {
                "company": row.get("company") or row.get("公司") or "",
                "language": row.get("language") or row.get("语言") or "",
                "role": row.get("role") or row.get("岗位") or "",
                "project": row.get("project") or row.get("项目") or "",
            }
            if text.strip():
                rows.append({"source": source, "url": url, "title": title, "text": text, "hints": hints})
    return rows


def build_records(raw_rows: list[dict], save_full_text: bool) -> list[dict]:
    records = []
    for row in raw_rows:
        qs = split_questions(row["text"])
        pqs = [q for q in qs if is_project_question(q)]
        c = classify(row["title"], row["text"], qs, pqs, row.get("hints", {}))
        records.append({
            "source": row["source"],
            "url": row["url"],
            "title": row["title"],
            "text_excerpt": row["text"] if save_full_text else row["text"][:3000],
            "questions": qs[:80],
            "project_questions": pqs[:80],
            "classification": asdict(c),
        })
    return records


def write_outputs(records: list[dict], out: Path) -> None:
    (out / "records.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    fields = "source difficulty super_hard_score company role language round projects enterprise_tags project_question_count title url".split()
    with (out / "summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for r in records:
            c = r["classification"]
            writer.writerow({
                "source": r["source"],
                "difficulty": c["difficulty"],
                "super_hard_score": c["super_hard_score"],
                "company": "|".join(c["companies"]),
                "role": "|".join(c["roles"]),
                "language": "|".join(c["languages"]),
                "round": "|".join(c["rounds"]),
                "projects": "|".join(c["projects"]),
                "enterprise_tags": "|".join(c["enterprise_tags"]),
                "project_question_count": c["project_question_count"],
                "title": r["title"],
                "url": r["url"],
            })
    write_bank(records, out / "project_grilling_bank.md")
    write_model(records, out / "grilling_model.md")


def write_bank(records: list[dict], path: Path) -> None:
    lines = ["# Project-Grilling Bank", "", "Keep source URLs. Distill patterns before publishing.", ""]
    for r in sorted(records, key=lambda x: x["classification"]["super_hard_score"], reverse=True):
        if not r["project_questions"]:
            continue
        c = r["classification"]
        lines += [
            f"## {r['source']} | {c['difficulty']} | {','.join(c['companies']) or 'Unknown Company'} | {','.join(c['roles']) or 'Unknown Role'} | {','.join(c['languages']) or 'Unknown Language'}",
            f"Source: {r['url']}",
            f"Projects: {', '.join(c['projects']) or 'unknown'}",
            f"Tags: {', '.join(c['enterprise_tags']) or 'none'}",
            "",
        ]
        lines += [f"- {q}" for q in r["project_questions"]] + [""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_model(records: list[dict], path: Path) -> None:
    source_counts = Counter(r["source"] for r in records)
    tag_counts = Counter(t for r in records for t in r["classification"]["enterprise_tags"])
    group_tags: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    group_examples: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for r in records:
        c = r["classification"]
        companies = c["companies"] or ["Unknown Company"]
        roles = c["roles"] or ["Unknown Role"]
        langs = c["languages"] or ["Unknown Language"]
        for key in [(companies[0], roles[0], langs[0])]:
            group_tags[key].update(c["enterprise_tags"])
            group_examples[key] += r["project_questions"][:3]

    lines = ["# Grilling Model", "", "## Corpus Summary", ""]
    lines += [f"- Records: {len(records)}"]
    lines += [f"- Sources: {', '.join(f'{k}={v}' for k, v in source_counts.items()) or 'none'}"]
    lines += [f"- Top enterprise tags: {', '.join(f'{k}={v}' for k, v in tag_counts.most_common(12)) or 'none'}", ""]
    lines += ["## Company / Role / Language Clusters", ""]
    for key, counts in sorted(group_tags.items(), key=lambda kv: sum(kv[1].values()), reverse=True)[:30]:
        company, role, lang = key
        tags = [t for t, _ in counts.most_common(5)]
        lines += [f"### {company} | {role} | {lang}", "", f"Focus tags: {', '.join(tags) or 'none'}", ""]
        for tag in tags:
            lines.append(f"- {DRILL_TEMPLATES.get(tag, '把候选人的项目说法压到机制、失败、指标和取舍。')}")
        for q in list(dict.fromkeys(group_examples[key]))[:5]:
            lines.append(f"- Source-style question: {q}")
        lines.append("")

    lines += ["## Universal Super-Hard Ladders", ""]
    for tag, template in DRILL_TEMPLATES.items():
        lines += [f"- **{tag}**: {template}"]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Collect and distill interview experiences into project-grilling data.")
    p.add_argument("--source", default="generic", choices=["nowcoder", "xiaohongshu", "generic"])
    p.add_argument("--seed-url", action="append", default=[])
    p.add_argument("--url-file", type=Path)
    p.add_argument("--raw-dir", type=Path)
    p.add_argument("--csv-file", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("data/interview-corpus"))
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

    raw_rows = []
    seeds = args.seed_url + read_url_file(args.url_file)
    if seeds:
        raw_rows += collect_urls(seeds, args)
    raw_rows += load_raw_dir(args.raw_dir, args.source)
    raw_rows += load_csv(args.csv_file, args.source)
    if not raw_rows:
        print("Provide URL seeds, --raw-dir, or --csv-file.", file=sys.stderr)
        return 2

    records = build_records(raw_rows, args.save_full_text)
    write_outputs(records, args.out_dir)
    counts = Counter(r["classification"]["difficulty"] for r in records)
    print(json.dumps({"records": len(records), "difficulty_counts": counts, "out_dir": str(args.out_dir)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
