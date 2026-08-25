# Claim Audit

Use this reference when the candidate provides a resume bullet, project description, or polished achievement. The goal is to detect packaging, inflated ownership, and shallow enterprise understanding.

Do not accuse the candidate of lying. Convert every suspicious claim into observable evidence.

## Audit Loop

For each claim, ask:

1. **Scope**: What exact business problem, user scenario, and success metric does this claim refer to?
2. **Ownership**: Which artifact did the candidate personally change: code path, table, interface, model, dashboard, rollout, document, incident response, or decision?
3. **Mechanism**: Can the candidate explain the critical path without naming only tools?
4. **Counterfactual**: What would have been different if the candidate was not on the project?
5. **Failure**: What broke or nearly broke, and how was it detected?
6. **Proof**: What number, log, trace, experiment, review comment, or incident record supports the claim?

If the answer stays vague for two turns, switch from "what did you do" to "show me one concrete object".

## Common Inflated Claims

### "负责核心模块"

Pressure:

- Which files, APIs, tables, dashboards, or rollout steps did you personally own?
- What decision did you make that another engineer could reasonably disagree with?
- Which part was owned by someone else?
- What would your tech lead say was your actual contribution?

Red flags:

- Only describes the whole system.
- Uses "we" for all hard parts and "I" for the result.
- Cannot name a rejected alternative.

### "优化性能 / QPS 提升"

Pressure:

- Baseline, final value, measurement method, time window, traffic shape, and bottleneck.
- Did P99, error rate, success rate, cost, and business metric move together?
- What else could explain the improvement?
- Which optimization hurt another metric?

Red flags:

- Only reports average latency.
- Cannot separate压测、灰度、线上真实流量.
- Has no denominator or confidence window.

### "高并发 / 分布式 / 架构升级"

Pressure:

- What was the real peak QPS, payload size, hot key, DB write rate, MQ backlog, and dependency timeout rate?
- Which component breaks first at 10x traffic?
- What is the degradation strategy and who can trigger it?
- What data can be lost, duplicated, reordered, or made stale?

Red flags:

- Treats adding Redis/MQ as the answer.
- Cannot describe failure under retry or duplicate delivery.
- No alert threshold or rollback owner.

### "保证一致性 / 幂等"

Pressure:

- What is the state machine?
- Who is the source of truth?
- What is the idempotency key, who generates it, where is it stored, and when does it expire?
- What happens when the idempotency record succeeds but the business write fails?
- How do compensation and manual repair avoid repeating the damage?

Red flags:

- Only says "Redis setnx".
- No DB unique constraint, transaction boundary, or state transition.
- Cannot handle late messages or duplicate callbacks.

### "项目上线 / 灰度 / 稳定性"

Pressure:

- What were the rollout batches, observation window, rollback condition, and owner?
- Which technical and business metrics were watched?
- What breaks if rollback crosses schema, message, cache key, or client versions?
- Which feature flag can stop bleeding, and who can operate it?

Red flags:

- Watches only CPU and error rate.
- No business metric such as conversion, payment success, retention, or manual intervention.
- Rollback plan ignores data compatibility.

### "AI / 推荐 / LLM 效果提升"

Pressure:

- What is the baseline and why is it fair?
- Which online metric can be gamed by the model?
- Where can leakage, label delay, sample drift, or traffic shift enter?
- How do bad cases become model, rule, data, prompt, or product changes?
- What is the fallback when model output is wrong but already affected a user?

Red flags:

- Only names model or framework.
- Confuses offline score with business value.
- No rollback plan for generated decisions.

## Packaging Severity

Use these labels internally when judging an answer:

- **Green**: Concrete artifact, clear metric, known failure branch, honest boundary.
- **Yellow**: Real participation but fuzzy metric, limited ownership, or weak recovery.
- **Orange**: Likely team-level packaging; candidate knows concepts but not project-specific decisions.
- **Red**: Inflated or fabricated signal; story changes under follow-up, no artifact, no mechanism, no ownership.

## Interviewer Moves

When a candidate overclaims:

```text
我先把范围收窄。你不要讲整个团队方案，只讲你亲手负责的那一个接口/表/状态/任务。输入是什么，输出是什么，失败会留下什么脏状态？
```

When a candidate hides behind "we":

```text
我相信团队做了这件事。但这轮我要判断你个人的 level。哪个决定如果没有你，会明显不同？
```

When a metric sounds too clean:

```text
这个数字听起来太整齐了。统计口径是什么？有没有反例、分层下降、观测窗口太短、或者业务自然波动？
```

When the answer is honest but incomplete:

```text
这个边界你没参与可以。那我换成推理题：如果现在你接手这个模块，第一天会补哪三个观测点，为什么？
```

## Debrief Language

Use evidence-based wording:

- Strong: "候选人能把 claim 落到具体状态机、指标和恢复动作，ownership 可信。"
- Mixed: "候选人可能真实参与过项目，但核心指标和失败恢复解释不足，像执行者而不是 owner。"
- Weak: "候选人主要在复述团队架构，无法证明个人决策、指标口径和线上风险处理。"
- Red flag: "多次追问后仍无法给出 artifact、状态、数字或边界，存在明显包装风险。"
