# Project Grilling Core

Use this reference for Resume/Project Grilling and intense project deep dives. It contains patterns promoted from the v0.4 evidence corpus: 140 public Nowcoder records, 95 real interview-experience records, 528 evidence-layer project questions, and about 243k evidence excerpt characters.

The goal is not to ask more questions. The goal is to turn every project claim into a concrete production scenario.

## Core Loop

For every project claim, run this loop:

1. **Reality**: What business problem existed, who needed it, and what metric made it worth solving?
2. **Ownership**: Which decision, code path, dashboard, incident, rollout, or trade-off did the candidate personally own?
3. **Mechanism**: How does the data/request/state flow through the system?
4. **Failure**: What breaks under timeout, retry, duplicate write, hot key, slow DB, dependency failure, release bug, or bad data?
5. **Metric**: Which metric proves the answer: QPS, P99, error rate, backlog, correctness rate, cost, conversion, money delta, or manual intervention count?
6. **Recovery**: How to detect, stop bleeding, rollback, compensate, reconcile, verify, and prevent recurrence?
7. **Trade-off**: What does the solution sacrifice: latency, consistency, cost, user experience, engineering speed, or operational simplicity?

If the candidate answers with generic components, ask for threshold, state, ownership, and failure branch.

## Promoted Drills

### Project Reality Audit

Use when a resume project sounds polished, generic, or overclaimed.

Opening:

```text
这个项目真实解决的业务问题是什么？不是技术栈，不是“提升体验”，我要听谁在什么场景下遇到了什么问题，以及你用什么指标证明它值得做。
```

Follow-ups:

1. 这个指标的 baseline 是多少，最终是多少，统计口径是什么？
2. 哪个模块是你亲手设计或实现的？说到类、接口、表、任务、dashboard 或发布动作。
3. 如果你离开项目，哪一个决策会不同？
4. 这个项目如果去掉“高并发、分布式、架构”这些词，真实难点还剩什么？
5. 你有没有亲手处理过线上 bug、报警、回滚、补偿或数据修复？

Red flags:

- Only describes team architecture.
- Cannot name a metric denominator, time window, or baseline.
- Says "负责" but cannot point to a decision or artifact.
- Claims high concurrency without traffic shape or bottleneck evidence.

### Failure-First Architecture

Use after the candidate explains a design too smoothly.

Opening:

```text
先不讲正常链路。假设这个系统今晚流量涨 10 倍，同时 Redis 有热 key，DB P99 飙升，下游接口 30% 超时。你判断哪里先崩，怎么止血？
```

Follow-ups:

1. 第一张 dashboard 看什么？网关、应用、Redis、DB、MQ、下游还是业务指标？
2. 是限流、降级、扩容、切缓存、回滚、暂停入口，还是关闭部分功能？
3. 止血后怎么确认没有造成脏数据、漏单、重复扣减或消息丢失？
4. 如果只能保一个核心功能，牺牲哪个非核心能力？
5. 事故后你会改代码、容量、监控、发布流程还是业务规则？

Red flags:

- Only says "加机器".
- Only prevents failure, cannot handle already broken state.
- No priority between user experience and correctness.

### Source Of Truth Drill

Use for cache, MQ, DB, client state, order/payment/inventory/coupon/account systems.

Opening:

```text
这条链路里谁是事实源？Redis、DB、MQ 消息、第三方支付回调、客户端状态、还是后台任务？如果它们冲突，谁覆盖谁？
```

Follow-ups:

1. 状态机有哪些合法状态和非法状态？
2. 哪些状态可以回退，哪些只能补偿，哪些必须人工介入？
3. 对账任务扫什么维度，多久扫一次，怎么避免重复修复？
4. 如果用户已经看到了错误状态，恢复后怎么通知或纠正体验？
5. 事实源切换或版本升级时，老数据怎么兼容？

Red flags:

- Treats cache as source of truth without invalidation/rebuild plan.
- Has no illegal-state definition.
- "定时任务修" but no scan key, no idempotency, no audit.

### Retry Storm Drill

Use when a candidate mentions retry, MQ, gateway, idempotency, or distributed calls.

Opening:

```text
假设客户端重复点击，网关超时重试，服务内部也重试，MQ 又重复投递。四层重复同时发生，你怎么保证不会重复写、重复扣、重复发？
```

Follow-ups:

1. 幂等键是什么？由谁生成？保存在哪里？有效期多久？
2. 并发请求同时查不到幂等记录时，会不会一起写入？
3. 重复请求返回第一次结果、当前状态，还是错误？
4. 幂等记录过期后，迟到消息来了怎么办？
5. 幂等设计会不会阻挡合法补偿或人工修复？

Red flags:

- Only says "Redis setnx" without DB unique constraint or state machine.
- No answer for concurrent first writes.
- No lifecycle for idempotency records.

### Release Business Regression Drill

Use when the project has deployment, gray release, A/B experiment, feature flag, or online metrics.

Opening:

```text
灰度发布后，错误率、CPU、P99 都正常，但下单转化率、点击率或留存开始掉。你怎么判断是发布问题、实验问题、流量问题还是业务自然波动？
```

Follow-ups:

1. 观察窗口多长？分桶维度是什么？
2. 技术指标正常时，业务指标从哪里采集？
3. 回滚会不会造成数据结构、消息格式、缓存 key 或客户端版本不兼容？
4. feature flag 谁能改，有没有审计和回滚？
5. 如果业务方催上线，你用什么证据决定继续、暂停或回滚？

Red flags:

- Only watches technical metrics.
- No rollback compatibility plan.
- Cannot separate A/B experiment from gray release impact.

### AI/Data Contract Drill

Use for algorithm, ML, recommendation, search, risk control, LLM, data platform, or BI projects.

Opening:

```text
别先讲模型。先讲数据契约：上游给你什么字段，延迟多久，可能怎么脏、怎么缺、怎么重复？这些问题会怎样污染你的结果？
```

Follow-ups:

1. 线上指标和离线指标分别是什么？哪个可能骗人？
2. 如何区分模型效果提升、样本变化、流量变化、标注变化和数据泄漏？
3. 上游数据迟到、乱序、重复、schema 变更时，下游怎么防？
4. 模型或规则回滚时，已经写入的业务状态怎么处理？
5. 如何监控 drift、bad case、召回异常和业务损失？

Red flags:

- Only names model or framework.
- No data quality checks.
- No rollback plan for generated decisions or downstream state.

### Frontend/Client Chain Trace Drill

Use for frontend, mobile, desktop, game/client, real-time UI, low-code, or platform projects.

Opening:

```text
从用户一次点击开始，完整讲出客户端状态、请求、接口、后端状态、埋点和错误展示的链路。哪里会重复、乱序、丢失或展示旧状态？
```

Follow-ups:

1. 慢网络、重复点击、接口部分失败时，UI 展示什么？
2. 前端状态和后端状态不一致时，谁纠正谁？
3. 首屏、交互延迟、内存、FPS 或包体积怎么量化？
4. 错误监控如何关联用户、页面、接口和后端 trace？
5. 如果后端回滚或接口字段变更，客户端怎么兼容？

Red flags:

- Only discusses component implementation.
- No user-visible failure handling.
- No observability from client to backend.

## Company-Style Pressure

Use company labels as weak priors, not stereotypes.

- **ByteDance**: Push on scale, system design, fast failure diagnosis, metrics, ownership, and whether the project survives 10x traffic.
- **Alibaba/Ant**: Push on business state, transaction boundaries, release process, stability, cross-team collaboration, and long-term maintainability.
- **Tencent**: Push on boundaries, protocol choices, C++/client/runtime constraints, real-time behavior, and design clarity.
- **Meituan**: Push on practical implementation, local life/order systems, cache/DB pressure, rollout, and business metric changes.
- **JD/PDD**: Push on order/payment/inventory/coupon/refund correctness, abuse risk, replay, idempotency, and senior challenge.
- **Huawei/Baidu/Kuaishou**: Push on engineering fundamentals plus production awareness: deployment, observability, capacity, reliability, and device/model/runtime constraints.

## Role-Specific Pivots

- **Backend**: state machine, data consistency, cache/MQ/DB ownership, throughput, release, observability.
- **Frontend**: user action chain, client state, stale data, repeated clicks, performance metrics, error tracing.
- **Algorithm/ML**: data contract, online/offline metric mismatch, drift, bad cases, model rollback, inference latency.
- **Data**: upstream quality, schema change, late/duplicate data, lineage, reconciliation, SLA, downstream business impact.
- **Testing/QA**: failure injection, test data, coverage boundaries, production escape, rollback verification.
- **Security/Risk**: abuse path, privilege boundary, replay, audit trail, sensitive data, false positive/negative cost.
- **Client/C++**: memory lifetime, thread safety, crash recovery, frame rate, device budget, protocol boundary.
- **Infra/SRE**: alerting, incident command, capacity, blast radius, rollback, multi-region, postmortem action.

## Scoring Signals

Strong answers:

- Name concrete metrics and thresholds.
- Explain a state machine or data flow without buzzwords.
- Include the broken case, not only the happy path.
- Own a specific decision or artifact.
- Recover already-corrupted state.
- Admit uncertainty and propose verification.

Weak answers:

- Recite components without business state.
- Cannot explain what fails first.
- Has prevention but no recovery.
- Cannot separate personal work from team work.
- Treats "high concurrency" as a label instead of measured load.
- Solves everything with cache/MQ/scale-out without trade-offs.
