# JSON Schema 与验证范围

每个 schema 对应 `person.json` 或 `data/` 下同名 JSON 文件。类型、必填字段、枚举、模式和未知字段限制均写在 schema 中；数据约定见 [DATA](../docs/DATA.md)。

这些是 JSON Schema 2020-12 格式的文件。本项目只用其中一个受控子集：`type`、`required`、`properties`、`additionalProperties`、`items`、`minItems`、`uniqueItems`、`minLength`、`minimum`、`enum`、`pattern`、`format`，以及 `$schema`、`title`、`description` 注释。

`research.py` 内置仅用于这些 schema 的轻量检查器，不声称实现完整 JSON Schema 规范。遇到未知 schema 关键字会报错而不是静默放过。`format` 只检查本项目的 `date` 与 `uri`。

程序另外检查真实日历日期、日期精度、唯一 ID/URL、跨表引用、模式的来源覆盖、路径与本地 Markdown 文件链接。它不验证外部网页是否可用，不验证引用足以支持主张，不判断历史事实、人格或版权。

预测与实验当前是空数组；schema 和模板用于将来真实登记，不代表本库已有预测回测或实验结果。
