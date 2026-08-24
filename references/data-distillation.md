# Data Distillation

Use `scripts/nowcoder_collect.py` to collect public Nowcoder interview-experience pages and convert them into skill-training material.

## Collection Rules

- Collect only public pages.
- Respect robots.txt and low request rates.
- Do not automate login, CAPTCHA solving, paywall bypassing, private messages, or account-restricted content.
- Keep source URLs for attribution.
- Prefer paraphrasing and pattern extraction before publishing distilled question banks.

## Recommended Command

```bash
python scripts/nowcoder_collect.py \
  --seed-url "https://www.nowcoder.com/discuss" \
  --max-pages 30 \
  --delay 3 \
  --out-dir data/nowcoder
```

If discovery pages are dynamic, provide direct detail URLs:

```bash
python scripts/nowcoder_collect.py \
  --url-file data/nowcoder_urls.txt \
  --max-pages 100 \
  --out-dir data/nowcoder
```

If the crawler returns no candidate detail URLs, first assume the seed page is dynamic or blocked by robots. Use direct public detail URLs collected manually from the browser, reduce `--max-pages`, keep `--delay` at 3 seconds or higher, and do not bypass access controls.

## Outputs

- `records.jsonl`: one JSON object per page, including title, URL, excerpts, extracted questions, project questions, and classification.
- `summary.csv`: sortable table with company, role, language, round, enterprise tags, project question count, and difficulty.
- `project_grilling_bank.md`: grouped project-question bank for manual review and later skill distillation.

## Classification Axes

- Company: ByteDance, Alibaba, Tencent, Meituan, JD, Huawei, PDD, Baidu, Kuaishou, Microsoft, Google, Amazon, and similar aliases.
- Language: Java, C++, Python, Go, JavaScript/TypeScript, C#, Rust.
- Role: backend, frontend, algorithm/ML, data, testing, client, infra/SRE, security, product.
- Round: first, second, third, HR, cross/extra round.
- Enterprise tags: high concurrency, consistency, idempotency, MQ, cache, database, availability, observability, release, security, cost, order/payment.
- Difficulty: normal, hard, super_hard.

## Super-Hard Project Signal

Treat a question as high-value when it forces the candidate to reason about production-grade failure, not textbook recall:

- 10x traffic, hot keys, peak traffic, backpressure.
- Timeout, retry, duplicate requests, duplicate consumption, idempotency.
- Data inconsistency, reconciliation, compensation, distributed transactions.
- Online incidents, rollback, monitoring, alerting, root-cause analysis.
- Cache avalanche/breakdown/penetration, big key, hot key.
- Deadlocks, lock contention, slow queries, index failure, sharding.
- Degradation, circuit breaking, rate limiting, disaster recovery.

Distill these into interviewer moves:

1. State the candidate's project claim.
2. Add a production constraint or failure.
3. Ask for detection, prevention, fallback, and recovery.
4. Demand metrics, ownership, and trade-offs.
5. Ask what would break first at the next scale tier.
