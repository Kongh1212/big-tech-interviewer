# Distilled Strategy

Use this reference to convert the distilled corpus into live interviewer behavior. The corpus is ammunition; this file is the firing plan.

## Interview Control

In project grilling, do not ask a list. Run a pressure chain:

```text
claim -> metric -> ownership -> mechanism -> failure -> recovery -> trade-off -> level judgment
```

Stay on one chain until the candidate either gives strong evidence or exposes a gap. Switch chains only after extracting signal.

## 50 High-Frequency Project Templates

Pick the closest template and adapt it to the candidate's project.

1. QPS/latency improvement without clear denominator.
2. Redis cache added to protect DB.
3. MQ used for async processing or peak shaving.
4. Order/payment/inventory state machine.
5. Idempotency for repeated clicks, callbacks, retries, or duplicate messages.
6. Gray release or feature flag rollout.
7. Rollback with schema, cache, message, or client compatibility risk.
8. Database lock contention or slow query under traffic.
9. Hot key, cache penetration, cache breakdown, or cache avalanche.
10. Distributed transaction replaced by eventual consistency.
11. Data reconciliation or compensation task.
12. Observability dashboard and alert threshold.
13. Dependency timeout, circuit breaker, fallback, or degradation.
14. Batch job with late, duplicate, or missing data.
15. Data metric definition disputed by business.
16. A/B experiment with misleading aggregate result.
17. Recommendation/search metric improvement.
18. Model/data drift after launch.
19. Badcase analysis and feedback loop.
20. LLM/RAG answer quality, hallucination, retrieval miss, or eval.
21. Frontend performance improvement.
22. Client state inconsistent with backend state.
23. Low-code schema design and version compatibility.
24. Undo/redo, conflict, concurrent editing, or autosave.
25. Error monitoring from client to backend trace.
26. Mobile/desktop crash on low-end devices.
27. C++ memory/threading/race bug.
28. Protocol compatibility across old and new versions.
29. Auth, permission, or越权 risk.
30. Replay, credential stuffing, abuse, or risk control.
31. Sensitive data logging, masking, audit, or deletion.
32. Test automation that claims quality improvement.
33. Production escape and release gate failure.
34. Pressure test that does not match real traffic.
35. Platform/middleware multi-tenant isolation.
36. Noisy-neighbor resource contention.
37. Cost optimization with reliability trade-off.
38. Storage growth, partitioning, archiving, or migration.
39. Search/indexing consistency and rebuild.
40. File/image/video processing pipeline.
41. Notification, IM, or realtime message ordering.
42. Offline/reconnect state repair.
43. Risk/manual review workflow.
44. Merchant/user/rider/order fulfillment exception.
45. SLA breach and incident command.
46. Cross-team dependency and delayed delivery.
47. Legacy refactor with no behavior regression.
48. Business metric moved but technical metric did not.
49. Technical metric moved but business metric did not.
50. Candidate claims leadership without decision evidence.

## Cross-Team Pressure

Use this when a project claims rollout, platform adoption, multiple business lines, design-system work, data metrics, or "推动落地".

Opening:

```text
这个项目涉及哪些团队？上游契约、下游影响、发布审批、回滚开关、事故指挥分别是谁负责？你个人推动了哪一条明确规则？
```

Follow-ups:

1. 产品、运营、后端、数据、QA、安全或设计系统团队里，谁的目标和你冲突最大？
2. 你们怎么定义上线标准：技术指标、业务指标、验收用例、灰度窗口还是人工审批？
3. 如果运营要求立刻上线，但后端说接口契约还不稳定，你用什么证据决策？
4. 失败发布后谁能一键回滚，谁通知用户，谁修数据，谁复盘？
5. 哪个协作规则最后沉淀成文档、CI gate、监控、权限或流程，而不只是口头约定？

## 20 Super-Hard Scenarios

Use these when normal follow-ups are too easy:

1. Redis hot key, DB P99 spike, MQ backlog, and downstream timeout happen at the same time.
2. Retry occurs at client, gateway, service, and MQ layers simultaneously.
3. Payment callback arrives before order creation is visible.
4. Gray release technical metrics are normal but conversion drops.
5. Rollback crosses schema/message/cache/client versions.
6. Compensation task repairs the same record twice.
7. Idempotency key expires before a delayed duplicate message arrives.
8. Cache rebuild produces stale data after DB repair.
9. A/B experiment aggregate improves while a key segment regresses.
10. Offline model metric improves but online retention drops.
11. Feature drift silently hurts cold-start users.
12. LLM fallback prevents hallucination but doubles latency/cost.
13. Low-code old schema is rendered by a new runtime after rollback.
14. Client optimistic update succeeds locally but backend rejects the operation.
15. Two tabs or clients overwrite each other's state.
16. Testing gate blocks a release because of a false positive during a business deadline.
17. Contract test passes but production data shape breaks the page.
18. A risk rule blocks real users and creates business loss.
19. Multi-tenant platform migration corrupts one tenant while global metrics look fine.
20. Incident stop-bleeding protects correctness but sacrifices user experience.

## 10 Company-Style Playbooks

- **ByteDance**: Start with scale and metrics, then attack failure diagnosis speed. Ask what breaks at 10x traffic and how the candidate proves impact.
- **Alibaba/Ant**: Start with business state and stability. Push transaction boundaries, release process, cross-team dependencies, and long-term maintainability.
- **Tencent**: Start with boundary clarity. Push protocol, client/runtime constraints, real-time behavior, C++ details, and ownership of design choices.
- **Meituan**: Start with practical implementation. Push order/local-life state, cache/DB pressure, rollout, and business metric movement.
- **JD**: Start with order/payment/inventory correctness. Push idempotency, refund, reconciliation, coupon abuse, and peak promotion traffic.
- **PDD**: Start with cost, speed, and abuse pressure. Push correctness under extreme trade-offs and whether shortcuts create second-order risk.
- **Huawei**: Start with engineering fundamentals and reliability. Push testability, deployment, observability, device/runtime constraints, and disciplined process.
- **Baidu**: Start with algorithm/search/data quality or infra fundamentals. Push online/offline mismatch, data lineage, serving latency, and rollback.
- **Kuaishou**: Start with recommendation/video/feed scenario. Push bad cases, cold start, content ecosystem side effects, and online metric validity.
- **Microsoft/Google/Meta/Amazon/Apple**: Start with first-principles reasoning and structured communication. Push ambiguity handling, design trade-offs, maintainability, and user impact.

## 10 Dangerous Answer Chains

Use these as "candidate says -> interviewer presses" mappings.

1. "我们用了 Redis" -> "缓存和 DB 冲突时谁是事实源？缓存如何重建，重建期间读到什么？"
2. "用了 MQ 削峰" -> "消息重复、乱序、积压、消费成功但 ack 失败分别怎么处理？"
3. "做了幂等" -> "幂等 key 生命周期是什么？并发首次请求和迟到消息怎么处理？"
4. "QPS 提升 5 倍" -> "入口 QPS、成功 QPS、P99、错误率、成本和业务转化分别怎么变？"
5. "有定时任务补偿" -> "扫什么维度，怎么防重复修，怎么审计，多久收敛？"
6. "灰度发布" -> "技术指标正常但业务指标下降，你怎么判断继续、暂停还是回滚？"
7. "模型效果提升" -> "如何排除样本变化、标注变化、数据泄漏、流量变化和分层反噬？"
8. "前端做了性能优化" -> "低端机、弱网、复杂页面、业务转化和错误率怎么同时验证？"
9. "测试覆盖率提升" -> "线上逃逸率、阻断率、误报率、回归耗时和人工成本怎么变化？"
10. "我推动落地" -> "谁反对，反对理由是什么，你用什么证据改变了决策？"
11. "支持多业务线" -> "哪几条业务线，差异是什么，谁有发布权限，回滚和指标归谁负责？"
12. "和后端/产品协作" -> "具体冲突是什么，最终规则写在哪里，出了事故谁能停流量？"

## Scoring Boundary

Use these boundaries in debriefs:

- **Hire**: Candidate gives concrete ownership, metric, mechanism, failure branch, recovery action, and trade-off. Some missing details are acceptable if reasoning is strong.
- **Lean hire**: Candidate likely did real work, but depth is uneven. They can reason through gaps when pressed.
- **Lean no hire**: Candidate knows concepts but cannot anchor them to their own project, metrics, or production consequences.
- **No hire**: Candidate repeatedly fails artifact, metric, mechanism, and ownership checks, or changes story under pressure.

## Promotion Rule

Do not promote every generated card into core skill behavior. Promote only patterns that meet at least two of these:

- Appears across multiple companies or roles.
- Forces concrete ownership.
- Exposes enterprise production risk.
- Produces a better follow-up after a vague answer.
- Helps distinguish real experience from packaging.
