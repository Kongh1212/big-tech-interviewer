# Big Tech Interviewer

一个面向中文/双语候选人的大厂面试官 Codex Skill。它的目标不是生成温和的普通面试题，而是模拟高标准面试官对项目、简历、系统设计、工程取舍和线上故障的持续追问。

核心方向：项目拷打、企业级场景、真实面经蒸馏。

## What It Does

- 进行高压但不羞辱的模拟面试
- 深挖简历和项目，区分真实负责与包装表达
- 按公司、岗位、语言、轮次和企业场景生成追问
- 从公开面经或用户提供材料中蒸馏项目拷打模型
- 将普通八股、题库合集和真实面经分层，避免错误训练

## Skill Modes

- `Interview Drill`: 一问一答式模拟面试
- `Resume/Project Grilling`: 简历和项目深挖
- `System/Coding/Product/Data Round`: 专项轮次
- `Debrief`: 回答复盘、评分和训练建议
- `Question Design`: 生成面试官问题集
- `Data Distillation`: 抓取/导入公开面经并蒸馏拷打模式

## Install

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/Kongh1212/big-tech-interviewer.git ~/.codex/skills/big-tech-interviewer
```

Restart Codex or reload skills, then trigger it with requests such as:

```text
用大厂面试官拷打我的项目
帮我做一轮字节 Java 后端项目深挖
根据这些牛客面经蒸馏项目拷打模型
```

## Corpus Distillation

The corpus pipeline lives in `scripts/interview_corpus.py`.

It supports:

- public Nowcoder URLs
- public Xiaohongshu URLs when accessible without login and allowed by robots
- manually exported Xiaohongshu/raw text files
- CSV files with columns such as `source,title,url,text,company,language,role,project`

Example:

```bash
python scripts/interview_corpus.py \
  --source nowcoder \
  --url-file data/nowcoder_urls.txt \
  --out-dir data/interview-corpus \
  --max-pages 50 \
  --delay 3
```

For Xiaohongshu or mixed sources, prefer manual exports:

```bash
python scripts/interview_corpus.py \
  --source xiaohongshu \
  --raw-dir data/raw-xhs \
  --out-dir data/interview-corpus
```

## Outputs

The pipeline writes:

- `records.jsonl`: classified records with excerpts, questions, project questions, and source URLs
- `summary.csv`: sortable table for source, source quality, company, role, language, tags, difficulty, and URL
- `project_grilling_bank.md`: project-question bank based mainly on real interview-experience evidence
- `grilling_model.md`: distilled company/role/language clusters and super-hard interviewer moves

## Source Quality

The pipeline separates corpus quality:

- `interview_experience`: concrete interview experience, suitable as primary evidence
- `question_compilation`: 八股、题库、合集、攻略, useful only as background reference
- `low_signal`: weak or unclear evidence

Only real interview-experience patterns should be promoted into the core interviewer behavior unless multiple sources confirm the same pattern.

## Ethical Collection Rules

- Collect only public pages or user-provided exports
- Respect robots.txt, low request rates, and platform access controls
- Do not automate login, CAPTCHA solving, paywall bypassing, or private-message access
- Keep source URLs for attribution
- Distill patterns and interviewer moves instead of publishing bulk copied source text

## Current Focus

The first corpus passes emphasize:

- ByteDance / Alibaba / Meituan / Tencent backend interviews
- Java, C++, Python, and Go
- high concurrency, MQ, cache, database, idempotency, consistency, release rollback, observability, cost, security, and order/payment failure cases

The long-term target is a reusable project-grilling model that can press any resume project from:

```text
claim -> mechanism -> edge case -> production failure -> metrics -> recovery -> trade-off -> ownership
```
