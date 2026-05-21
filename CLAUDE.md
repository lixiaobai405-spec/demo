## Auto Commit And Push Workflow
- 每次完成开发任务并通过可行验证后，自动执行 `commit + push`，除非我明确说不要提交或不要推送。
- commit 前必须运行 `git status` 和 `git diff`。
- 只提交本次任务相关文件，不提交无关改动。
- 不提交密钥、token、日志、缓存或临时文件。
- commit message 使用英文。
- 不允许 force push。