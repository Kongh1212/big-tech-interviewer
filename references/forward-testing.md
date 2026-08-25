# Forward Testing

Use this reference when improving or validating the skill itself. The goal is to verify interviewer behavior in realistic interview turns, not to admire the prompt.

## What To Test

Run forward tests against concrete candidate material:

- A resume bullet that may be inflated.
- A project summary with technical keywords but weak evidence.
- A role/company target, such as ByteDance backend, Meituan frontend, Alibaba algorithm, Tencent C++ client, or Huawei testing.
- A candidate answer style: vague, overconfident, junior, senior, evasive, or genuinely strong.

Prefer short independent tests over one huge test. Each test should reveal whether the skill asks sharper follow-ups after seeing the candidate's last answer.

## Test Scenarios

### Java Backend 秒杀/交易链路

Candidate claim:

```text
负责秒杀下单系统核心交易链路重构，引入 Redis 缓存、RocketMQ 异步削峰、库存预扣和订单状态机，QPS 提升 5 倍，支持大促峰值流量。
```

Expected pressure:

- Ask for baseline QPS, peak shape, P99, error rate, oversell/undersell, and conversion impact.
- Force a source-of-truth answer for库存、订单、支付、MQ 消息、缓存.
- Probe four-layer duplicate execution: repeated click, gateway retry, service retry, MQ duplicate delivery.
- Ask what breaks first when Redis hot key, DB P99, and MQ backlog happen together.
- Separate personal ownership from team architecture.

Failure signals:

- The interviewer jumps to generic Java basics before exhausting the project.
- It accepts "Redis + MQ + DB" as an answer without idempotency and state machine details.
- It does not ask how already-broken data is recovered.

### Frontend Low-Code / Complex State

Candidate claim:

```text
负责低代码平台画布和表单渲染模块，优化首屏性能和拖拽交互体验，支持多个业务线搭建活动页。
```

Expected pressure:

- Trace one user action from UI state to request, backend state, schema persistence, preview, publish, and rollback.
- Ask for low-end device performance, interaction latency, bundle size, error monitoring, and schema compatibility.
- Probe stale state, repeated operations, undo/redo, concurrent editing, and published-page回滚.
- Ask which abstraction the candidate personally designed.

Failure signals:

- The interviewer only asks React/Vue lifecycle or component trivia.
- It ignores product/business publishing state.
- It does not test schema evolution and rollback.

### Algorithm / Recommendation / LLM

Candidate claim:

```text
负责推荐排序模型优化，引入多路召回和特征工程，线上点击率提升 8%，并建设 badcase 分析流程。
```

Expected pressure:

- Ask for offline/online metrics, baseline, experiment bucket, confidence, and business side effects.
- Probe data leakage, label delay, traffic change, sample bias, and feature drift.
- Ask how bad cases become training data or rule changes.
- Ask how to rollback a model after it has affected user state or downstream decisions.

Failure signals:

- The interviewer only asks model names.
- It cannot distinguish model improvement from流量/样本/标注变化.
- It ignores inference latency and cost.

### Testing / QA Production Escape

Candidate claim:

```text
负责核心链路自动化测试和压测体系建设，提升回归效率，减少线上问题。
```

Expected pressure:

- Ask which线上问题 escaped before, why test missed it, and what changed after.
- Probe test data, environment parity, flaky cases, coverage boundary, and release gate.
- Ask how to verify rollback and data repair.
- Ask whether efficiency improvement sacrificed defect detection.

Failure signals:

- The interviewer only asks测试理论.
- It does not demand a production escape story.
- It accepts "覆盖率提升" without defect-rate or escape-rate evidence.

## Evaluation Rubric

Score each forward test from 1 to 5:

- **Project focus**: Stays anchored to the candidate's project instead of drifting to generic question banks.
- **Follow-up sharpness**: Each new question uses the candidate's previous answer to narrow the attack.
- **Enterprise realism**: Covers release, observability, rollback, consistency, idempotency, cost, or business metrics.
- **Ownership detection**: Distinguishes personal decisions from team/system claims.
- **Recovery pressure**: Tests what happens after data, state, or user experience is already wrong.

Pass threshold:

- Average score >= 4.
- No dimension below 3.
- At least one recovery question and one metric question appear in the first six interviewer turns.

Hard requirements for the first six interviewer turns:

- At least one metric-scope question: baseline, denominator, time window, P99, error rate, success rate, cost, conversion, or other measurable impact.
- At least one ownership question: personally owned module, code path, decision, rejected alternative, dashboard, incident, rollout, or review challenge.
- At least one duplicate-execution or consistency question when the project touches cache, MQ, DB, payment, inventory, orders, callbacks, or distributed calls.
- At least one already-broken-state recovery question: rollback, compensation, reconciliation, data repair, user correction, incident stop-bleeding, or postmortem action.
- No generic fundamentals question before the project claim has been exhausted, unless the candidate's own answer exposes a specific fundamental gap.

Fail the test if any hard requirement is missing.

## Improvement Loop

After each forward test:

1. Save the transcript or concise notes outside the skill folder unless it is a reusable golden example.
2. Identify the first turn where the interviewer became generic, too soft, or too broad.
3. Convert the missing behavior into a reusable rule, transcript pattern, or role-specific pressure point.
4. Update the smallest relevant reference file.
5. Re-run the same scenario and one different scenario to avoid overfitting.

## Review Checklist

Before calling a new version better, answer:

- Did it ask one question at a time in live interview mode?
- Did it avoid giving the ideal answer too early?
- Did it challenge vague words such as "负责", "优化", "高并发", and "落地"?
- Did it ask for numbers, thresholds, ownership artifacts, and failure branches?
- Did it handle both prevention and recovery?
- Did it end with hire/no-hire signal grounded in evidence?

## Encoding Check

Keep all skill Markdown files in UTF-8. If Chinese text appears as mojibake such as "鎷锋墦" or "闈㈢粡" in a normal UTF-8 read, fix the file before validating behavior. Terminal display glitches are acceptable only when a separate UTF-8 read shows correct Chinese.
