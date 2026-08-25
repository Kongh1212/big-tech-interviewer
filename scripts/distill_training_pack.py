#!/usr/bin/env python3
"""Generate a large distilled project-grilling training pack.

The output is derived from structured corpus metadata and enterprise tags. It
does not republish full source text; source URLs are kept for attribution.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


TAG_MOVES = {
    "high_concurrency": {
        "scene": "流量突然放大、热点请求集中、线程池和下游依赖被打满",
        "open": "你说项目能抗高并发。高并发具体是多少，峰值持续多久，压测模型和真实线上流量有什么差别？",
        "followups": [
            "流量涨 10 倍时，最先到瓶颈的是网关、应用线程池、Redis、DB、MQ 还是下游接口？证据是什么？",
            "限流加在哪里？按用户、IP、商户、接口、资源 ID 还是租户？误伤正常用户怎么办？",
            "压测数据怎么造？读写比例、热点分布、请求体大小、登录态、链路依赖有没有模拟？",
            "如果 P99 上升但平均响应正常，你会先看哪几个指标？",
            "扩容是横向加机器、拆热点、异步化、缓存预热还是降级？为什么？",
        ],
    },
    "cache": {
        "scene": "缓存热 key、击穿、穿透、雪崩、数据过期和 DB 回源压力",
        "open": "你说用了 Redis。它在你的项目里到底是性能优化、状态存储、分布式锁，还是业务事实源？",
        "followups": [
            "Redis 挂了以后，系统是直接失败、降级读 DB、返回旧值，还是切到本地缓存？",
            "热 key 怎么发现？是慢日志、命令统计、带宽、CPU、业务 key 维度，还是调用链指标？",
            "缓存和 DB 不一致时，用户会看到什么错误？你怎么修复已经读到脏数据的请求？",
            "缓存过期策略怎么定？为什么不是更长或更短？",
            "如何防穿透？布隆过滤器、空值缓存、参数校验各自的误判风险是什么？",
        ],
    },
    "database": {
        "scene": "慢查询、索引失效、锁竞争、事务过长、分库分表和数据迁移",
        "open": "你项目里数据库最核心的表是哪几张？主键、索引、状态字段和写入频率分别是什么？",
        "followups": [
            "一条 SQL 线上突然变慢，你从执行计划、索引、锁、数据量、参数分布哪个角度先查？",
            "这个索引为什么这样建？如果查询条件变化或者数据倾斜，会不会失效？",
            "事务边界在哪里？事务里有没有远程调用、批量更新或长时间持锁？",
            "分库分表后跨分片查询怎么做？分页、排序、聚合和扩容迁移怎么处理？",
            "如果线上已经出现死锁，你怎么定位哪两条链路互相等待？",
        ],
    },
    "mq": {
        "scene": "消息重复、丢失、乱序、积压、死信、重试和消费端恢复",
        "open": "你说用了 MQ。它解决的是削峰、解耦、异步通知、最终一致性，还是任务调度？",
        "followups": [
            "消息重复消费时，业务状态机会不会被推进两次？幂等点在哪里？",
            "消息积压以后，你怎么判断是生产太快、消费太慢、下游故障还是分区不均？",
            "消费失败重试几次？什么时候进死信？死信如何补偿回放？",
            "如果顺序消息被打乱，业务上哪个字段会错？",
            "生产成功但本地事务失败，或者本地事务成功但消息没发出去，怎么兜底？",
        ],
    },
    "idempotency": {
        "scene": "客户端重复点击、网关重试、服务重试、MQ 重复消费和并发写入",
        "open": "这个项目哪里必须保证幂等？幂等键是什么，生命周期多久，重复请求返回什么？",
        "followups": [
            "幂等键放在 Redis、DB 唯一索引、状态机还是业务流水表？为什么？",
            "如果两个请求同时打进来，先查后写会不会并发穿透？",
            "幂等记录过期后，迟到消息又来了怎么办？",
            "重复请求是返回第一次结果、当前状态，还是错误？调用方能接受吗？",
            "幂等方案会不会挡住合法重试或补偿任务？",
        ],
    },
    "consistency": {
        "scene": "订单、支付、库存、优惠券、积分、账户余额等多状态不一致",
        "open": "这条业务链路里谁是事实源？状态机有哪些合法状态和非法状态？",
        "followups": [
            "支付成功但订单失败，用户看到什么？系统怎么自动恢复？",
            "库存扣了但订单取消，补偿怎么保证不会重复返还？",
            "最终一致的最长窗口是多少？超过窗口谁报警？",
            "对账任务按什么维度扫？怎么区分可自动修复和必须人工介入？",
            "强一致和最终一致之间，你为什么选这个？业务能承受什么风险？",
        ],
    },
    "availability": {
        "scene": "依赖超时、服务降级、熔断、限流、容灾、多活和恢复",
        "open": "如果一个核心依赖 30% 请求超时，你的服务会怎么退化？用户能感知到什么？",
        "followups": [
            "超时时间怎么设？和重试次数、线程池、连接池之间怎么配合？",
            "熔断后返回默认值、旧数据、排队等待还是直接失败？为什么？",
            "降级开关谁能开？有没有灰度、审计和回滚？",
            "多机房或多可用区故障时，状态数据怎么切？",
            "恢复服务时如何避免流量瞬间打爆刚恢复的依赖？",
        ],
    },
    "observability": {
        "scene": "线上事故、报警、日志、指标、链路追踪和根因定位",
        "open": "如果线上已经出事，你能在 10 分钟内靠哪些指标定位到模块和责任链路？",
        "followups": [
            "报警是按错误率、P99、业务量、队列积压、DB 慢查询还是用户投诉触发？",
            "日志里有没有 request id、user id、order id、trace id？如何串起来？",
            "如果技术指标正常但业务指标掉了，你看什么？",
            "根因定位后，怎么证明不是误判？",
            "复盘里你会改监控、流程、代码还是容量？优先级怎么排？",
        ],
    },
    "release": {
        "scene": "灰度发布、批次发布、回滚、开关、AB 实验和业务指标异常",
        "open": "你们项目怎么发布？灰度比例、观察窗口、回滚条件和负责人是谁？",
        "followups": [
            "第一批发布后 CPU 或负载异常但随后恢复，你继续、暂停还是回滚？",
            "技术指标没问题但转化率下降，怎么判断是否和发布有关？",
            "回滚会不会造成数据结构、消息格式或缓存 key 不兼容？",
            "Feature flag 放在哪里？谁能改？有没有审计？",
            "AB 实验和灰度发布同时存在时，如何避免结论互相污染？",
        ],
    },
    "security": {
        "scene": "越权、刷单、重放、敏感数据、审计、风控和权限边界",
        "open": "这个项目最容易被滥用的接口是哪一个？攻击者会怎么利用？",
        "followups": [
            "权限校验在前端、网关、服务层、数据层分别做了什么？",
            "如果用户篡改 orderId、tenantId 或 userId，能不能读到别人的数据？",
            "重放请求怎么防？签名、时间戳、nonce 和幂等之间怎么配合？",
            "敏感字段在哪里脱敏？日志、缓存、导出文件会不会泄露？",
            "发现刷单或异常退款后，如何追溯证据链？",
        ],
    },
    "cost": {
        "scene": "容量、资源利用率、存储、计算、带宽、复杂度和维护成本",
        "open": "如果要求成本下降 30%，但核心 SLA 不变，你先动哪一块？",
        "followups": [
            "哪些资源是过度预留，哪些是不能动的安全水位？",
            "缓存、异步化、批处理、冷热分层哪个收益最大？证据是什么？",
            "降成本会牺牲延迟、可用性、准确率还是研发效率？",
            "有没有因为过度设计导致的维护成本？",
            "如果删掉一个组件，系统会更简单还是更脆弱？",
        ],
    },
    "order_payment": {
        "scene": "订单、支付、库存、优惠券、退款、结算和状态机",
        "open": "订单链路从创建到支付成功，中间有哪些状态？哪些状态不能回退？",
        "followups": [
            "用户支付成功但订单超时关闭，系统如何恢复？",
            "优惠券锁定、库存扣减和支付确认的顺序为什么这样排？",
            "退款重复提交时，资金和订单状态怎么保证一致？",
            "结算任务失败后，商户侧和用户侧分别看到什么？",
            "人工改单有没有审计和二次确认？",
        ],
    },
}

DEFAULT_TAGS = ["database", "cache", "high_concurrency", "release", "observability", "cost"]


def load_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def labels(items: list[str], fallback: str) -> str:
    return " / ".join(items[:3]) if items else fallback


def build_card(index: int, record: dict, tag: str) -> str:
    c = record["classification"]
    move = TAG_MOVES[tag]
    company = labels(c["companies"], "Unknown Company")
    role = labels(c["roles"], "Unknown Role")
    lang = labels(c["languages"], "Unknown Language")
    tags = c["enterprise_tags"] or DEFAULT_TAGS
    neighboring = [t for t in tags if t != tag][:4]
    neighbor_text = "、".join(neighboring) if neighboring else "项目真实性、指标、恢复路径、个人负责"
    source = record.get("url") or "unknown"
    title = record.get("title") or "untitled"
    followups = move["followups"]
    lines = [
        f"## Card {index:04d}: {company} | {role} | {lang} | {tag}",
        "",
        f"Evidence source: {source}",
        f"Evidence title: {title}",
        "",
        f"场景抽象：{move['scene']}。",
        f"关联压力点：{neighbor_text}。",
        "",
        f"开场拷打：{move['open']}",
        "",
        "连续追问：",
    ]
    for i, q in enumerate(followups, 1):
        lines.append(f"{i}. {q}")
    lines += [
        "",
        "听答案时抓这几类信号：",
        "1. 有没有明确指标：QPS、P99、错误率、积压量、成本、转化率、资金差错率或人工介入量。",
        "2. 有没有真实边界：峰值、热点、超时、失败、脏数据、重复请求、版本兼容或权限边界。",
        "3. 有没有恢复闭环：发现、止血、回滚、补偿、对账、验证、复盘。",
        "4. 有没有个人所有权：候选人亲自做过的代码、设计、排查、监控、发布或协调。",
        "",
        "危险回答：",
        "- 只说“加缓存、加 MQ、加限流”，但讲不出阈值、状态、失败分支和指标。",
        "- 把团队已有架构说成个人设计，却无法解释关键取舍。",
        "- 只讲预防，不讲已经出事以后如何恢复。",
        "- 只讲技术组件，不讲业务后果和用户感知。",
        "",
        "继续加压：",
        f"- 如果这个项目迁移到 {company} 的真实生产环境，流量、组织协作、数据规模和发布风险会放大在哪里？",
        f"- 如果候选人只能保留一个设计选择，必须删除一个组件，保留什么、删除什么、为什么？",
        f"- 如果面试官要求 5 分钟内给出事故处理方案，第一条命令、第一张 dashboard、第一位协作对象分别是什么？",
        "",
    ]
    return "\n".join(lines)


def write_pack(records: list[dict], out: Path, target_chars: int) -> None:
    evidence = [r for r in records if r["classification"].get("source_quality") == "interview_experience"]
    evidence.sort(key=lambda r: (r["classification"].get("difficulty") != "super_hard", -r["classification"].get("super_hard_score", 0)))

    quality = Counter(r["classification"].get("source_quality", "unknown") for r in records)
    difficulty = Counter(r["classification"].get("difficulty", "unknown") for r in records)
    tags = Counter(t for r in evidence for t in r["classification"].get("enterprise_tags", []))
    companies = Counter(x for r in evidence for x in r["classification"].get("companies", []))
    roles = Counter(x for r in evidence for x in r["classification"].get("roles", []))
    langs = Counter(x for r in evidence for x in r["classification"].get("languages", []))

    lines = [
        "# Big Tech Interviewer Distilled Training Pack",
        "",
        "This pack is distilled from structured corpus metadata and project-question signals. It keeps source URLs for attribution but avoids republishing full interview-experience text.",
        "",
        "## Corpus Stats",
        "",
        f"- Records: {len(records)}",
        f"- Evidence records: {len(evidence)}",
        f"- Source quality: {', '.join(f'{k}={v}' for k, v in quality.items())}",
        f"- Difficulty: {', '.join(f'{k}={v}' for k, v in difficulty.items())}",
        f"- Top companies: {', '.join(f'{k}={v}' for k, v in companies.most_common(12))}",
        f"- Top roles: {', '.join(f'{k}={v}' for k, v in roles.most_common(12))}",
        f"- Top languages: {', '.join(f'{k}={v}' for k, v in langs.most_common(10))}",
        f"- Top enterprise tags: {', '.join(f'{k}={v}' for k, v in tags.most_common(12))}",
        "",
        "## How To Use This Pack",
        "",
        "Use each card as an interviewer behavior pattern. Start from the candidate's project claim, pick the closest enterprise tag, ask the opening question, then keep following until the candidate gives mechanisms, metrics, failure handling, recovery, trade-offs, and personal ownership.",
        "",
        "## Distilled Cards",
        "",
    ]

    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in evidence:
        for tag in record["classification"].get("enterprise_tags", []) or DEFAULT_TAGS:
            if tag in TAG_MOVES:
                grouped[tag].append(record)

    idx = 1
    tag_order = [tag for tag, _ in tags.most_common()] + [t for t in DEFAULT_TAGS if t not in tags]
    while len("\n".join(lines)) < target_chars:
        added = False
        for tag in tag_order:
            bucket = grouped.get(tag) or evidence
            if not bucket:
                continue
            record = bucket[(idx - 1) % len(bucket)]
            lines.append(build_card(idx, record, tag if tag in TAG_MOVES else DEFAULT_TAGS[0]))
            idx += 1
            added = True
            if len("\n".join(lines)) >= target_chars:
                break
        if not added:
            break

    text = "\n".join(lines)
    out.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a distilled project-grilling training pack.")
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--target-chars", type=int, default=100_000)
    args = parser.parse_args()
    records = load_records(args.records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_pack(records, args.out, args.target_chars)
    print(json.dumps({"out": str(args.out), "chars": len(args.out.read_text(encoding="utf-8"))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
