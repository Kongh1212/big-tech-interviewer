# Role Tracks

Use the relevant track when the user specifies a role or round. Adapt examples to the candidate's level.

## Business-Line Selection

When the project is concrete, choose a business-line lens before asking deep questions. This makes the interview feel like a real team interview instead of a generic technical screen.

- **Transaction / Order / Payment**: order state machine, inventory, payment callback, refund, reconciliation, idempotency, fraud, money correctness.
- **Ads / Growth / Marketing**: bidding, pacing, attribution, conversion, anti-spam, experiment validity, budget waste, delayed feedback.
- **Recommendation / Search / Feed**: recall, ranking, feature freshness, cold start, drift, bad cases, online/offline mismatch, latency and cost.
- **IM / Realtime / Collaboration**: ordering, delivery semantics, reconnect, offline messages, presence, fanout, conflict resolution, client consistency.
- **Local Life / Fulfillment / Logistics**: dispatch, capacity, ETA, merchant/user/rider state, exception handling, compensation, SLA.
- **Risk / Security / Account**: identity, permission boundary, replay, abuse path, false positive/negative cost, audit and rollback.
- **Developer Platform / Low-Code / Internal Tools**: schema evolution, permission, publishing, rollback, tenant isolation, observability, migration.
- **Infra / Middleware / Data Platform**: SLO, capacity, multi-tenant isolation, backpressure, data lineage, late data, recovery and cost.

Opening move:

```text
你这个项目我先按 <business-line> 来问。这个场景里最不能错的业务状态是什么？如果它错了，损失怎么被发现、止血和修复？
```

Cross-team pressure:

- Which team owned the upstream contract, downstream behavior, release approval, rollback switch, and incident command?
- Which rule was negotiated with product, operations, design, data, security, QA, or backend teams?
- If two teams disagree on speed vs correctness, what evidence decides?
- During a failed release, who has authority to stop traffic, roll back, notify users, and repair data?

## Backend / Infrastructure

Probe:

- API design, data modeling, concurrency, caching, queues, consistency, idempotency.
- Reliability: timeout, retry, circuit breaker, rollback, disaster recovery, observability.
- Scale: QPS, storage growth, hot keys, partitioning, backpressure, cost.
- Business-line fit:
  - Transaction/order: legal state transitions, duplicate callbacks, reconciliation, refund and compensation.
  - Ads/growth: delayed conversion, budget overspend, experiment leakage, anti-spam.
  - Platform/middleware: multi-tenant isolation, noisy neighbor, quota, compatibility, migration.

Strong follow-ups:

- What breaks first at 10x traffic?
- How do you prevent duplicate processing?
- What is the consistency model?
- What would your alert fire on?
- Which state cannot be rolled back and must be compensated?
- What is the first stop-bleeding action during an incident?

## Frontend

Probe:

- Component architecture, state management, rendering performance, accessibility, browser compatibility.
- Product judgment: user flow, experiment design, design-system trade-offs.
- Reliability: error boundaries, monitoring, feature flags, rollback.
- Business-line fit:
  - Low-code/platform: schema versioning, published-page rollback, editor state conflict, permission boundary.
  - Transaction UI: repeated click, stale order state, payment result correction, user-visible compensation.
  - Realtime/collaboration: offline/reconnect, ordering, conflict, optimistic update rollback.
  - Cross-team: operations publishing rules, design-system constraints, backend API contract, data/analytics event ownership, QA release gates.

Strong follow-ups:

- Why this state boundary?
- How did you measure interaction latency?
- What happened on low-end devices?
- How did you prevent design drift?
- If backend state and UI state conflict, who corrects whom?
- How do client errors connect to backend trace and business loss?
- If operations, backend, and data teams disagree during a bad publish, who owns rollback and user correction?

## Machine Learning / AI

Probe:

- Problem formulation, labels, data leakage, feature quality, evaluation, online/offline mismatch.
- Deployment: latency, monitoring, drift, human feedback, safety, cost.
- LLM work: retrieval quality, prompt/version control, eval design, hallucination handling.
- Business-line fit:
  - Recommendation/search: recall loss, ranking side effects, feature freshness, cold start, diversity.
  - Risk: false positive/negative cost, manual review, adversarial change, auditability.
  - LLM/RAG: retrieval miss, grounding, eval set drift, prompt/version rollout, fallback and human escalation.

Strong follow-ups:

- What is the baseline and why?
- Where can leakage enter?
- Which metric aligned with business value?
- How did you handle bad cases in production?
- Which offline metric lied to you?
- How do you rollback a model after it affected user or business state?

## Data / Analytics

Probe:

- Metric definitions, denominator choice, cohorting, attribution, experiment validity.
- SQL/data modeling, pipeline reliability, data quality, stakeholder communication.
- Enterprise reality: schema changes, late data, duplicate events, lineage, SLA, downstream dashboards and decisions.

Strong follow-ups:

- What exactly is the denominator?
- How do you know this was causal?
- Which segment moved and which did not?
- What data quality issue would invalidate the conclusion?
- If yesterday's data is wrong after leaders already made a decision, how do you correct, notify, and prevent recurrence?

## Product Manager

Probe:

- User problem, prioritization, trade-offs, launch strategy, metrics, cross-functional influence.
- Ambiguity handling, conflict, and post-launch learning.

Strong follow-ups:

- Why this user segment first?
- What did you choose not to build?
- Which metric could be gamed?
- What would make you kill the feature?
- If engineering says the reliable version takes twice as long, what scope do you cut?

## Engineering Manager / Tech Lead

Probe:

- Team diagnosis, project sequencing, technical debt, hiring, performance management, stakeholder alignment.
- Mechanisms for execution, not slogans.

Strong follow-ups:

- What behavior changed after your intervention?
- Who disagreed and why?
- How did you know the team was healthier?
- What decision created second-order cost?
- Which technical debt did you deliberately keep, and what guardrail prevented it from becoming an incident?
- Which cross-team contract did you make explicit so the project did not rely on verbal agreement?

## Testing / QA

Probe:

- Production escape, test data, contract testing, release gate, flaky tests, coverage boundary, environment parity.
- Pressure testing: traffic model, bottleneck attribution, data correctness under load, rollback verification.
- Quality economics: defect escape rate, blocking rate, false alarm cost, regression time, manual cost.

Strong follow-ups:

- Which escaped defect changed your test strategy?
- What did your tests still fail to cover?
- How do you prove quality improved rather than releases becoming smaller?
- How do you verify rollback and data repair after a failed release?

## Security / Risk

Probe:

- Authentication, authorization, replay, privilege boundary, sensitive data, audit trail, abuse model.
- Risk trade-offs: false positive/negative cost, manual review, user friction, attacker adaptation.

Strong follow-ups:

- Show me the cheapest abuse path.
- Which permission boundary did you personally design?
- How do you detect replay or credential stuffing without hurting normal users?
- If a bad rule blocked real users, how do you rollback and compensate?

## Client / C++

Probe:

- Memory lifetime, thread safety, crash recovery, frame budget, device constraints, protocol compatibility.
- Realtime state: reconnect, partial update, local cache, old client/new server compatibility.

Strong follow-ups:

- Which object owns this memory and when is it released?
- What happens during reconnect with stale local state?
- How do you reproduce and triage a crash seen only on low-end devices?
- Which protocol field can never be removed?

## Coding Round

Run the round like a real interviewer:

1. Ask the candidate to restate the problem.
2. Require examples and edge cases.
3. Ask for brute force first if useful.
4. Push for complexity analysis.
5. Add constraints or hidden edge cases after an initial solution.
6. Ask for test cases and failure modes.

Do not provide the solution before the candidate attempts it.
