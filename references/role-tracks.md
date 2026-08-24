# Role Tracks

Use the relevant track when the user specifies a role or round. Adapt examples to the candidate's level.

## Backend / Infrastructure

Probe:

- API design, data modeling, concurrency, caching, queues, consistency, idempotency.
- Reliability: timeout, retry, circuit breaker, rollback, disaster recovery, observability.
- Scale: QPS, storage growth, hot keys, partitioning, backpressure, cost.

Strong follow-ups:

- What breaks first at 10x traffic?
- How do you prevent duplicate processing?
- What is the consistency model?
- What would your alert fire on?

## Frontend

Probe:

- Component architecture, state management, rendering performance, accessibility, browser compatibility.
- Product judgment: user flow, experiment design, design-system trade-offs.
- Reliability: error boundaries, monitoring, feature flags, rollback.

Strong follow-ups:

- Why this state boundary?
- How did you measure interaction latency?
- What happened on low-end devices?
- How did you prevent design drift?

## Machine Learning / AI

Probe:

- Problem formulation, labels, data leakage, feature quality, evaluation, online/offline mismatch.
- Deployment: latency, monitoring, drift, human feedback, safety, cost.
- LLM work: retrieval quality, prompt/version control, eval design, hallucination handling.

Strong follow-ups:

- What is the baseline and why?
- Where can leakage enter?
- Which metric aligned with business value?
- How did you handle bad cases in production?

## Data / Analytics

Probe:

- Metric definitions, denominator choice, cohorting, attribution, experiment validity.
- SQL/data modeling, pipeline reliability, data quality, stakeholder communication.

Strong follow-ups:

- What exactly is the denominator?
- How do you know this was causal?
- Which segment moved and which did not?
- What data quality issue would invalidate the conclusion?

## Product Manager

Probe:

- User problem, prioritization, trade-offs, launch strategy, metrics, cross-functional influence.
- Ambiguity handling, conflict, and post-launch learning.

Strong follow-ups:

- Why this user segment first?
- What did you choose not to build?
- Which metric could be gamed?
- What would make you kill the feature?

## Engineering Manager / Tech Lead

Probe:

- Team diagnosis, project sequencing, technical debt, hiring, performance management, stakeholder alignment.
- Mechanisms for execution, not slogans.

Strong follow-ups:

- What behavior changed after your intervention?
- Who disagreed and why?
- How did you know the team was healthier?
- What decision created second-order cost?

## Coding Round

Run the round like a real interviewer:

1. Ask the candidate to restate the problem.
2. Require examples and edge cases.
3. Ask for brute force first if useful.
4. Push for complexity analysis.
5. Add constraints or hidden edge cases after an initial solution.
6. Ask for test cases and failure modes.

Do not provide the solution before the candidate attempts it.
