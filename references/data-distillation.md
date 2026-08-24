# Data Distillation

Use `scripts/interview_corpus.py` to collect or ingest public interview-experience material from Nowcoder, Xiaohongshu, and generic exported text, then convert it into skill-training material. Use `scripts/nowcoder_collect.py` only for legacy Nowcoder-only runs.

## Collection Rules

- Collect only public pages or user-provided exports.
- Respect robots.txt and low request rates.
- Do not automate login, CAPTCHA solving, paywall bypassing, private messages, or account-restricted content.
- Keep source URLs for attribution.
- Prefer paraphrasing and pattern extraction before publishing distilled question banks.
- For Xiaohongshu, prefer manual export to `--raw-dir` or `--csv-file` unless a public URL can be fetched without login and robots.txt allows it.

## Recommended Command

```bash
python scripts/interview_corpus.py \
  --source nowcoder \
  --seed-url "https://www.nowcoder.com/discuss" \
  --max-pages 30 \
  --delay 3 \
  --out-dir data/interview-corpus
```

If discovery pages are dynamic, provide direct detail URLs:

```bash
python scripts/interview_corpus.py \
  --source nowcoder \
  --url-file data/nowcoder_urls.txt \
  --max-pages 100 \
  --out-dir data/interview-corpus
```

If the crawler returns no candidate detail URLs, first assume the seed page is dynamic or blocked by robots. Use direct public detail URLs collected manually from the browser, reduce `--max-pages`, keep `--delay` at 3 seconds or higher, and do not bypass access controls.

For Xiaohongshu or mixed sources, use manual exports:

```bash
python scripts/interview_corpus.py \
  --source xiaohongshu \
  --raw-dir data/raw-xhs \
  --out-dir data/interview-corpus
```

Or use CSV with columns such as `source,title,url,text,company,language,role,project`:

```bash
python scripts/interview_corpus.py \
  --csv-file data/interview_experiences.csv \
  --out-dir data/interview-corpus
```

## Outputs

- `records.jsonl`: one JSON object per page, including title, URL, excerpts, extracted questions, project questions, and classification.
- `summary.csv`: sortable table with source, company, role, language, project terms, round, enterprise tags, project question count, and difficulty.
- `project_grilling_bank.md`: grouped project-question bank for manual review and later skill distillation.
- `grilling_model.md`: deterministic distilled model with source mix, company/role/language clusters, dominant enterprise tags, and super-hard follow-up templates.

After generating `grilling_model.md`, read `references/grilling-model.md` to decide which patterns deserve promotion into the core interviewer behavior.

## Classification Axes

- Company: ByteDance, Alibaba, Tencent, Meituan, JD, Huawei, PDD, Baidu, Kuaishou, Microsoft, Google, Amazon, and similar aliases.
- Language: Java, C++, Python, Go, JavaScript/TypeScript, C#, Rust.
- Role: backend, frontend, algorithm/ML, data, testing, client, infra/SRE, security, product.
- Source: Nowcoder, Xiaohongshu, generic, or user-provided CSV/raw exports.
- Project terms: extracted from phrases such as "项目是..." and optional CSV `project` hints.
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
