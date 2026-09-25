# 上传到自己的 GitHub

建议仓库名：`fanbing-research`。中文显示标题为“范冰研究”，系列名为“人物研究计划 / People Research”。

## 最稳妥的方式

在 GitHub 新建**空仓库**，不要预建 README、LICENSE 或 `.gitignore`。解压 ZIP，进入包含 README 与 `person.json` 的目录。先执行本地校验，再使用 Git：

```bash
cd fanbing-research
python scripts/research.py validate
python -m unittest discover -s tests -v

git init
git add .
git commit -m "init: add source-grounded Fan Bing research"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fanbing-research.git
git push -u origin main
```

将 `YOUR_USERNAME` 换成你的 GitHub 用户名。登录与认证使用你平时的 GitHub 配置；不要把 Token 写进文件或仓库地址。已有同名或非空仓库时，先确认分支和历史，不使用强制推送覆盖内容。

不会用命令行也可以用 GitHub Desktop：添加解压后的本地目录，提交后发布。浏览器直接上传时注意 `.github` 和 `.gitignore` 等隐藏文件；它们可能不会被操作系统普通选择动作带上。

## 发布前后要做的编辑

审阅 README 中的非官方与 AI 辅助说明；确认许可与范围。把 `person.json` 中的 `repository_url` 改为自己的正式地址，并按需要在 `CITATION.cff` 加上 `repository-code`。没有正式地址时留空，不提前冒用账号。

推荐 description：

```text
持续研究范冰（XDash）的公开博客、作品、实践与观点变化；从可追溯证据中提炼可检验的经验。Part of People Research.
```

可选 topics：`person-research`、`xdash`、`fanbing`、`knowledge-management`、`research-notes`、`agent-skills`。

## 原来的仓库怎么办

尚未上传旧包：直接使用本包。已上传旧包：把新版放到新的工作分支，审阅差异后合并，不必丢弃历史；如果确实要修改 GitHub 仓库名，使用 GitHub 设置再更新本地远程地址。

本包未替你创建远程仓库、推送内容、联系任何人或开启后台任务。
