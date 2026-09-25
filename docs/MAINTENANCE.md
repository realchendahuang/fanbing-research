# 维护与命令

## 环境

Python 3.11+，只使用标准库。没有密钥、联网安装、后台进程或自动爬虫。脚本生成的是文字视图，不会修改外部站点或账户。

## 命令

```bash
# 统计规范数据与实际阅读范围
python scripts/research.py stats

# 不区分大小写的普通文本检索：先查结构化记录，再查原创研究文档
python scripts/research.py search "写作"
python scripts/research.py search "newsletter" --limit 12

# 重建来源卡、目录、时间线、作品表、队列和 README 统计
python scripts/research.py build

# 检查数据结构、日期、跨表引用与本地链接
python scripts/research.py validate

# 不写文件，只检查生成视图是否是最新版本
python scripts/research.py build --check

# 测试工具和本库
python -m unittest discover -s tests -v
```

命令在项目根目录示范；也可以从其他目录以脚本的绝对路径调用。`--root` 放在子命令前，可用于校验另一份采用相同结构的研究库。

## 日常更新

选一个问题 → 阅读来源 → 记录实际范围 → 补来源和主张 → 检查时间线与反例 → 更新原创笔记 → `build` → `validate` → `build --check` → 单元测试 → 人工审阅差异。

更新资料核对日期时，同时检查 `person.json` 的 `as_of` 与更新日志。不要更新旧条目的 `checked_at` 假装重新打开过网页。

## 常见错误

`unknown reference` 表示 ID 不存在；先补记录而非删除引用。日期精度错误通常来自给未知年份补造月日，或未同步 `date_precision`。本地链接不存在时核对大小写，Linux / GitHub 对大小写可能比本地更严格。

`generated file differs` 表示视图未重建或被手工改动。修改数据源后运行 `build`；不要长期同时维护两份来源卡。数据校验通过不代表外链当前可用。

## GitHub Actions

附带离线 CI，在 push 和 pull request 时运行检查，不定时访问研究对象网站。工作流只需读取仓库，无外部密钥。模板依据 GitHub 官方 Python Actions 指南，参考日期 2026-09-25：[官方指南](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)。

CI 必须在你自己的 GitHub 仓库启用 Actions 后才会运行；本 ZIP 仅包含配置，本地测试不等于远端 CI 已通过。
