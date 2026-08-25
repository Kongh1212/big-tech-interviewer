# Interview Transcripts

Use these transcripts as behavioral examples. They are distilled examples, not copied source material. Follow the pacing: one focused question, candidate answer, judgment, sharper follow-up.

## Java Backend: 秒杀交易链路

Frame: ByteDance/Meituan backend, mid-level, project deep dive, intensity 8/10.

```text
面试官：
你简历写“负责秒杀下单系统核心交易链路重构，QPS 提升 5 倍”。先别讲 Redis 和 MQ。原始问题是什么，baseline 是多少，最终指标怎么量的？

候选人：
之前高峰期下单比较慢，后来我们用了缓存和 MQ，QPS 从大概几千提升到一万多。

判断：vague
追问：
“几千”和“一万多”不够。峰值持续多久？P99、错误率、下单成功率、超卖/少卖分别是多少？统计口径是压测、灰度还是线上真实流量？

候选人：
压测是 1.2w QPS，线上大促峰值大概 8k，P99 我记得 200ms 左右，错误率没太关注。

判断：risky
追问：
交易链路你不关注错误率很危险。假设客户端重复点击，网关超时重试，服务内部重试，MQ 又重复投递，四层重复同时发生，怎么保证不重复扣库存、不重复建单？

候选人：
我们用了 Redis setnx 做幂等，订单也有状态机。

判断：acceptable
追问：
幂等 key 是谁生成的？存在 Redis 还是 DB？两个并发请求同时 setnx 成功前后，DB 有没有唯一约束兜底？如果 Redis key 过期后 MQ 迟到消息来了，系统返回什么状态？

候选人：
key 是用户 id 加活动 id，Redis 里有过期时间，DB 订单表应该也有唯一索引。

判断：vague
追问：
“应该有”不算。你亲手改的是哪一段？库存预扣、订单状态机、MQ 消费、还是幂等表？说一个你做过的具体决策，以及当时 rejected 的另一个方案。

候选人：
我主要做 MQ 消费和订单状态流转，当时没有直接同步扣库存，因为高峰会打爆 DB。

判断：acceptable
追问：
那我们只看 MQ 消费。消费成功但订单创建失败、订单创建成功但 ack 失败、支付回调先到但订单还没落库，这三个状态分别怎么处理？谁是事实源？

候选人：
订单表是事实源，库存会有补偿任务，支付回调如果查不到订单会重试。

判断：acceptable
追问：
补偿任务扫什么？按订单状态、库存流水、MQ 消息表还是支付流水？多久扫一次？怎么保证补偿本身不会重复修、修错、或者把合法失败订单补成成功？

候选人：
这个细节我没有完全参与，只知道有定时任务处理。

判断：honest gap
追问：
可以。那你负责的订单状态机里，哪些状态能回退，哪些只能补偿，哪些必须人工介入？如果今晚线上出现 1000 单支付成功但订单状态未更新，你第一张 dashboard 看什么，第一条止血动作是什么？
```

Good interviewer behavior:

- It attacks metrics before architecture.
- It does not accept Redis/MQ as magic words.
- It turns a vague ownership claim into a specific module.
- It reaches already-corrupted state recovery within six turns.

## Frontend: 低代码平台画布和发布链路

Frame: Alibaba/Tencent frontend, mid-level, project deep dive, intensity 7/10.

```text
面试官：
你说负责低代码平台画布和表单渲染模块。不要先讲组件封装，从用户一次拖拽开始，讲完整链路：客户端状态、schema、接口、保存、预览、发布和埋点。

候选人：
用户拖组件后会更新画布状态，然后保存成 JSON schema，后端存起来，发布时渲染页面。

判断：vague
追问：
拖拽中、拖拽结束、自动保存、手动保存分别改哪份状态？本地状态和后端 schema 不一致时，谁覆盖谁？

候选人：
本地会先乐观更新，保存失败就提示用户，后端是最终状态。

判断：acceptable
追问：
保存失败时用户已经继续拖了 5 个组件，你是整体回滚、局部标红、重新合并，还是阻塞后续编辑？如果两个 tab 同时编辑同一个页面，怎么处理冲突？

候选人：
我们主要是单人编辑，没有做多人协同。两个 tab 的情况可能后保存覆盖前保存。

判断：risky
追问：
那发布态有没有版本号？如果后保存覆盖前保存，线上页面已经发布了旧 schema，回滚时回到哪个版本？业务方怎么知道这次发布影响了哪个活动页？

候选人：
发布有版本记录，可以按版本回滚，活动页有 id。

判断：acceptable
追问：
版本记录是完整 schema 快照还是 diff？schema 字段升级后，旧版本回滚会不会被新渲染器解释错？你怎么做兼容？

候选人：
我们给 schema 加了 version，不同 version 走不同解析逻辑。

判断：strong
追问：
说一个你亲手设计的兼容策略。比如字段删除、组件重命名、默认值变化、后端接口字段变化，哪一种最容易造成线上旧页面异常？监控怎么发现？

候选人：
组件重命名比较危险，我们做了 alias 映射，渲染错误会上报页面 id、组件 type 和 schema version。

判断：strong
追问：
性能优化你说“首屏提升”。baseline 是什么，最终是多少？低端机、弱网、复杂 schema 下分别怎么测？如果埋点显示技术加载变快但发布转化没变，你怎么解释？
```

Good interviewer behavior:

- It avoids drifting into framework trivia.
- It treats low-code as a publishing and compatibility system.
- It probes user-visible failure and business impact.

## Algorithm/AI: 推荐排序与 Badcase

Frame: ByteDance/Kuaishou algorithm, mid-level, project deep dive, intensity 8/10.

```text
面试官：
你说推荐排序点击率提升 8%。先别讲模型。这个 8% 是离线 AUC、线上 CTR、还是某个业务转化？实验桶、周期、置信度和对照组怎么设计？

候选人：
是线上 CTR，A/B 大概跑了一周，实验组比对照组高 8%。

判断：acceptable
追问：
一周里流量分布有没有变化？新用户、老用户、冷启动用户、不同频道是否都涨？有没有某些分层下降但总量上涨？

候选人：
主要整体涨了，分层我记得新用户效果一般。

判断：vague
追问：
新用户效果一般为什么还能上线？你们优化目标是总 CTR、留存、时长、GMV，还是长期满意度？哪个指标可能被 CTR 提升反噬？

候选人：
目标主要是 CTR 和时长，可能会影响内容多样性。

判断：acceptable
追问：
那数据契约是什么？上游给哪些特征，延迟多久，缺失、重复、乱序、schema 变更时排序服务会怎么退化？

候选人：
有用户画像、内容特征、实时行为，缺失时会用默认值。

判断：vague
追问：
默认值会不会造成某类用户被系统性低估？你怎么发现这是特征缺失，而不是模型本身差？监控看特征覆盖率、分布 drift，还是 badcase 标签？

候选人：
我们有特征覆盖率监控，也会看 badcase。

判断：acceptable
追问：
badcase 怎么进入下一轮改进？人工标注、规则修复、训练样本重加权、特征修复，还是召回策略调整？谁判断这个 badcase 值得修？

候选人：
产品和算法一起看，严重的会加规则或者补样本。

判断：acceptable
追问：
如果规则修了 badcase 但导致推理延迟 P99 超预算，或者让某类内容曝光骤降，你怎么决策上线、灰度、回滚？已经影响用户曝光的数据要不要修？
```

Good interviewer behavior:

- It attacks metric validity before model complexity.
- It checks whether the candidate understands data contracts.
- It asks about side effects, rollback, and downstream state.

## Testing/QA: 自动化与线上逃逸

Frame: Huawei/Alibaba testing or QA, mid-level, project deep dive, intensity 7/10.

```text
面试官：
你说建设自动化测试和压测体系，减少线上问题。先讲一个真实线上逃逸：什么 bug 没测出来，为什么漏了，造成了什么影响？

候选人：
有一次接口变更导致页面异常，因为回归没有覆盖到那个场景。

判断：vague
追问：
哪个接口、哪个字段、哪个页面、多少用户受影响？是测试用例缺失、测试数据不对、环境不一致，还是发布门禁失效？

候选人：
是订单列表接口字段变了，测试环境数据没有覆盖历史订单，所以没发现。

判断：acceptable
追问：
那你后来的自动化改动是什么？新增用例、构造数据、契约测试、mock 校验、还是发布前 diff 检查？你亲手做了哪一个？

候选人：
我做了接口契约测试和历史订单数据构造。

判断：strong
追问：
契约测试谁维护契约？后端改字段时如何阻断？如果业务确实需要 breaking change，测试体系怎么区分合理变更和事故？

候选人：
契约在仓库里，CI 会跑，breaking change 需要评审和同步前端。

判断：acceptable
追问：
压测体系怎么和这个逃逸问题有关？压测主要发现性能问题，它不能证明字段兼容。你怎么避免把“回归效率提升”和“质量提升”混成一个指标？

候选人：
回归效率看执行时间，质量看线上缺陷数和逃逸率。

判断：strong
追问：
线上缺陷数下降可能只是发布少了或者统计口径变了。你的 denominator 是版本数、需求数、用例数、用户流量，还是事故等级？怎么证明是你的体系有效？

候选人：
这个我没有严格做因果，只按版本统计过。

判断：honest gap
追问：
好，那如果现在要你补一个更可信的质量指标体系，你会怎么设计？至少给出逃逸率、阻断率、误报率、回归耗时和人工成本之间的取舍。
```

Good interviewer behavior:

- It forces the candidate to start from production escape, not testing slogans.
- It distinguishes efficiency metrics from quality metrics.
- It tests whether QA understands release gates and business risk.

## Using These Examples

When running a live interview:

1. Borrow the shape of the transcript, not the exact wording.
2. Keep only one active attack path at a time.
3. If the candidate becomes specific, go deeper on that path.
4. If the candidate becomes vague, ask for metric, owner, artifact, state, or failure branch.
5. If the candidate admits a gap honestly, do not punish immediately; switch to reasoning under uncertainty.
