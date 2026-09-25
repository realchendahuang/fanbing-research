# 范冰研究 · Fan Bing Research

**研究公开作品，理解长期变化，验证可借鉴的经验。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/realchendahuang/fanbing-research?style=social)](https://github.com/realchendahuang/fanbing-research)
[![GitHub forks](https://img.shields.io/github/forks/realchendahuang/fanbing-research?style=social)](https://github.com/realchendahuang/fanbing-research/network/members)
[![GitHub issues](https://img.shields.io/github/issues/realchendahuang/fanbing-research)](https://github.com/realchendahuang/fanbing-research/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/realchendahuang/fanbing-research/pulls)
[![Follow @realchendahuang](https://img.shields.io/badge/Follow-%40realchendahuang-1DA1F2?logo=x&logoColor=white)](https://x.com/realchendahuang)

`fanbing-research` 是「人物研究计划 / People Research」的一个独立实例。研究对象是 **范冰（XDash），《增长黑客》作者**；身份依据见 [对象卡](docs/SUBJECT.md)。这是非官方、非本人授权背书的研究项目，不是全集镜像、粉丝站、人格克隆或本人意见的代理。

这里关心的不只是“他说过什么”，也包括：他如何处理信息、写作、做工具、选择发布方式；这些做法怎样变化；哪些判断有反例；我们能怎样在自己的场景里检验它们。

> **版本 v0.2.0 · 本轮资料核对日期 2026-09-25。** 当前是 AI 辅助整理、尚待维护者人工复核的研究种子库。网页核对时间不保证源站实时刷新；收录范围不是“范冰全部历史”。

<!-- STATS:START -->
| 内容 | 当前数量与范围 |
| --- | --- |
| 来源记录 | 53，包含入口、目录及节目说明；不是全文已读篇数 |
| 有出处的主张 | 36，区分页面事实与本人自述 |
| 时间节点 | 30，保留日/月/年精度 |
| 作品与项目条目 | 14，注明本轮实际查看范围 |
| 原创案例 / 工作假设 | 8 / 5 |
| 待研究任务 | 12 |
| 已登记预测 / 实验 | 0 / 0；不为凑数编造结果 |
<!-- STATS:END -->

## 从哪里开始

| 你想做什么 | 推荐入口 |
| --- | --- |
| 先理解项目与主要发现 | [快速开始](START_HERE.md) → [研究综述](research/OVERVIEW.md) |
| 按历史阅读博客与作品 | [时间线](timeline/README.md) → [作品目录](works/README.md) → [来源目录](sources/README.md) |
| 提炼可借鉴的做法 | [八个案例](research/cases/README.md) → [五个待验证模式](research/patterns/README.md) → [迁移与实验](research/lessons/TRANSFER.md) |
| 检查结论是否站得住 | [证据主张表](research/CLAIMS.md) → [反例与张力](research/COUNTEREVIDENCE.md) → [覆盖缺口](research/GAPS.md) |
| 用 Agent 继续研究 | [Agent 指南](AGENTS.md) → [可移植 Skill](skills/person-research/SKILL.md) |
| 增补资料、参与系列 | [贡献规范](CONTRIBUTING.md) → [任务队列](research/QUEUE.md) → [系列复用](docs/SERIES.md) |

## 这版已经研究到哪里

选样从现存博客的 2009 年资料整理文章延伸到 2026 年的公开出版实践；这只是所选材料的时间跨度，不代表最早创作年份或逐年完整覆盖。[S013](sources/cards/S013.md) [S046](sources/cards/S046.md)

第一条研究线是长期的信息处理工作流，第二条是自用工具与写作实践，第三条是周刊、书籍、网站之间的交付变化。项目停止、写作代价和对公开构建的保留意见也纳入分析，避免只收集成功故事。支持证据与限制逐项见[综述](research/OVERVIEW.md)。

本库把“本人说自己这样做过”和“外部材料证明这件事”分开。五个模式只是工作假设，不是对其人格的判断，更不是已经验证的致富公式。

## 本地使用

需要 Python 3.11 或以上，无第三方依赖；不运行任何网页抓取或账号操作。

```bash
python scripts/research.py stats
python scripts/research.py search "信息"
python scripts/research.py validate
python -m unittest discover -s tests -v
```

编辑 `person.json`、`data/*.json` 或原创研究文档之后：

```bash
python scripts/research.py build
python scripts/research.py validate
python scripts/research.py build --check
```

macOS / Linux 上命令可能是 `python3`；Windows 可用 `py -3`。脚本可以从其他工作目录调用，默认自动定位本仓库。详细说明见[维护指南](docs/MAINTENANCE.md)。

## 数据与目录

```text
fanbing-research/
├── person.json                 # 对象、系列、版本与身份来源
├── data/                       # 来源、主张、事件、作品、模式等规范数据
├── schemas/                    # JSON Schema 与验证范围说明
├── sources/                    # 自动生成的来源目录与逐条来源卡
├── timeline/                   # 区分事件时间、发表时间的时间线
├── works/                      # 作品与项目目录，注明阅读范围
├── research/                   # 综述、案例、反例、模式、实验方案、更新记录
├── skills/person-research/     # 可移植人物研究 Skill，不是人格模拟器
├── templates/                  # 新资料、模式、案例、预测和实验模板
├── scripts/                    # 离线生成、检索、校验工具
├── tests/                      # 数据与工具测试
├── docs/                       # 发布、复用、对象边界与维护说明
└── .github/                    # Pull Request / Issue 模板与离线 CI
```

## 公开与版权边界

仅收录公开来源的链接、元数据和原创研究注释；不打包博客全文、书稿、付费内容或播客逐字稿。研究对象允许某些作品免费阅读，不代表许可所有再分发、商业使用或改授许可。[S042](sources/cards/S042.md) [S044](sources/cards/S044.md)

本库原创代码与文字适用 [MIT](LICENSE)，第三方内容及其权利不在此授权范围。详见 [NOTICE](NOTICE.md)。接受有证据的纠错；公开 Issue 中不要填写私人联系方式、无关家庭材料或其他敏感信息。

[English introduction](README.en.md) · [上传到 GitHub](docs/PUBLISH.md) · [研究方法](METHODOLOGY.md) · [更新记录](CHANGELOG.md)
