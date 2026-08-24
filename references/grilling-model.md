# Grilling Model

Use this reference after `scripts/interview_corpus.py` produces `grilling_model.md`.

## Model Structure

Treat the distilled model as a cluster map:

- Source: Nowcoder, Xiaohongshu, generic exports, or CSV.
- Company: the company bar and interview style signal.
- Role: backend, frontend, data, algorithm/ML, testing, client, infra/SRE, security, product.
- Language: Java, C++, Python, Go, JavaScript/TypeScript, C#, Rust.
- Project terms: project domain hints such as order system, risk control, payment, recommendation, data platform.
- Enterprise tags: production-grade failure and trade-off domains.
- Difficulty: normal, hard, super_hard.

## Distillation Loop

1. Start from a company/role/language cluster.
2. Pick the dominant enterprise tags.
3. Convert source-style questions into interviewer moves, not copied text.
4. Build a ladder: claim -> mechanism -> failure -> metric -> recovery -> trade-off -> ownership.
5. Prefer super-hard questions that force production reasoning over textbook recall.

## Interviewer Move Template

```text
你说你的项目是 <project>，在 <company/role/language> 这个场景下我会追：
如果 <enterprise failure>，你怎么发现、止血、恢复、验证、复盘？
继续追：这个方案的成本、边界、误判风险和你个人负责的决策是什么？
```

## Promotion Rule

Promote a pattern into the core skill only when it appears across multiple sources or has strong enterprise realism:

- It couples at least two enterprise tags, such as MQ + idempotency or cache + database.
- It forces a concrete metric or production signal.
- It asks for failure recovery, not only prevention.
- It distinguishes personal ownership from team output.
- It can be adapted across projects without copying source content.
