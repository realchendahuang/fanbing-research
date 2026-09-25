# 数据约定

规范数据位于 `person.json` 和 `data/*.json`；Markdown 来源卡与目录是可再生成的视图，不是第二套手工数据库。

| 文件 | 单位 | 关键字段 |
| --- | --- | --- |
| `person.json` | 一个研究对象 | `slug`、身份来源、研究边界、版本、`as_of` |
| `sources.json` | 一份可定位来源/入口 | URL、日期依据、阅读范围、来源性质、权利说明 |
| `claims.json` | 一条有限主张 | 类型、来源、定位、限制 |
| `timeline.json` | 一个事件或发表记录 | 日期、精度、日期性质、关联主张 |
| `works.json` | 一项作品/工具/项目 | 类型、来源、当前已观察范围 |
| `patterns.json` | 一个工作假设 | 支持与反向主张、案例组数、限制、削弱条件 |
| `reading-queue.json` | 一个研究问题 | 优先级、行动、来源线索、状态 |
| `predictions.json` | 可核对的公开预测 | 原始断言、日期、时间界限、验证条件、状态 |
| `experiments.json` | 使用者实际登记的实验 | 设计、基线、结果、局限、模式关联 |
| `review-log.json` | 一次研究批次 | 核对时间、版本、方法、人工复核状态、局限 |

## ID 与引用

来源 `S001`、主张 `C001`、事件 `E001`、作品 `W001`、模式 `P001`、任务 `Q001`，预测使用 `PR001`，实验使用 `X001`。追加新 ID，不因日期排序重新编号。ID 只在各自数据集中唯一；引用必须指向存在记录。

`patterns.source_ids` 应覆盖支持与反向主张实际使用的来源。来源的 `date_source_ids` 用来说明从哪一份目录或记录核对日期，而不是暗示它是独立证明。

## 阅读与可信度

`review_status` 只能使用 `page_read`、`partial_read`、`index_only`、`shownotes_only`；精确范围由 `verification_scope` 解释。需要新增音频已核听等状态时，先统一修改 schema、工具和文档，再登记真实阅读结果。

`evidence_origin` 区分本人发布、采访自述、平台目录和独立报道；本版没有把同一人的多个渠道当成独立来源。来源组用于提醒依赖，不自动算得分。

## 时间

`published_at` 允许 `null`、`YYYY`、`YYYY-MM`、`YYYY-MM-DD`。`date_precision` 必须匹配。事件 `date_role` 当前支持 `publication`、`retrospective_event`、`bibliographic`、`event`。正文落款与归档日期不一致时必须说明，不能悄悄选择一个。

## 空数据不是遗漏

当前预测和实验数据为空。没有明确可检验预测、没有执行实验，就不为凑齐目录生成示例“结果”。模板中的示例字段均为待填写要求，不属于数据。

## 校验范围

[schemas](../schemas/README.md) 提供机器可读结构。脚本检查本项目使用的 schema 子集、日期、重复记录、跨表 ID、本地文件路径和生成内容一致性；不发网络请求、不核验外链存活、不判断外部事实真假。
