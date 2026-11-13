# Dialogue Enhancer · 对话增强器

把 AI 的长回复变成可圈选、可批注的阅读界面，一次整理多个问题，再带回原会话追问。

A local reading and annotation companion for AI conversations. Select passages, collect questions, and copy one follow-up prompt back into the same conversation.

## 功能

- 自动读取本机 Codex、WorkBuddy 与 Claude Code 会话文本；Work / ChatGPT / 其他工具可手动粘贴。
- 左栏按来源和 session 分组，展开查看该会话的回复；支持深色模式，首次跟随系统，切换后记住选择。
- Markdown 排版：标题、加粗、列表、表格和代码块。
- 选中文字后自动出现意见输入框；支持全文意见。
- 可自定义的快捷提问气泡，默认“这是什么？”“写得更易懂些”“举个例子”。
- 生成的追问仅包含引用与意见，不重复整篇原回复。
- 草稿与气泡设置保存在浏览器中，支持 JSON 备份和导入。
- macOS 可安装后台常驻服务，登录启动、退出自动重启。

## 快速开始

需要 Python 3.9+ 和现代浏览器。无需 API key、无需安装 Python 依赖。前端库已随仓库提供，不依赖 CDN。

```sh
git clone https://github.com/joshuama2002zz-coder/dialogue-enhancer.git
cd dialogue-enhancer
python3 server.py
```

打开 **http://127.0.0.1:8765**。手动启动时请保持终端运行；按 Ctrl+C 停止。

通用启动方式适用于有 Python 的桌面系统；目前浏览器交互和后台服务主要在 macOS 上验证。

## macOS 常驻安装

在仓库目录执行：

```sh
python3 manage_service.py install
python3 manage_service.py status
```

程序复制到 `~/Library/Application Support/DialogueEnhancer`，登录后自动启动，意外退出后重启。关闭终端或 Codex 不影响服务。电脑关机、睡眠或用户退出登录期间不可访问。

源码更新后，再执行 `python3 manage_service.py install` 即可同步运行副本。

卸载自启动（保留程序文件与浏览器草稿）：

```sh
python3 manage_service.py uninstall
```

配置位于 `~/Library/LaunchAgents/local.dialogue-enhancer.plist`；日志位于 `~/Library/Logs/DialogueEnhancer/`。安装脚本会更新同名服务；请避免同时手动运行另一份服务器。

## 使用

1. 在左侧选择回复，或粘贴一条回复。
2. 选中一段文字，直接在右侧写意见；点击气泡可填入预设问题，已有内容时会追加。
3. 想评论整体内容时，点击“全文意见”。右上角“设置”可以增删修改气泡。
4. 生成并复制 Prompt，粘贴回**同一个 AI 会话**。

**快捷键：**页面任意位置按 Esc 删除最近操作的标注，否则删除最后一条。连续按可逐条删除，按住不会连续删除；有弹窗时会同时关闭弹窗。选中卡片后也可以按 Delete / Backspace 删除，编辑文字时删除键只删文字。误删可使用页面上的“撤销”。

## 数据与边界

- 服务器只监听 `127.0.0.1:8765`，不上传对话、不调用模型、不自动发消息。不要通过公网代理暴露此服务：它没有账户认证，会读取当前用户的本地对话。
- 默认扫描 `~/.codex/sessions` 和 `~/.codex/archived_sessions`，也可通过 `CODEX_HOME` 环境变量指定目录；每 3 秒重新读取。大量历史记录可能影响性能。
- 只读取标记为 `final_answer` / `final` 的 assistant 最终文本，忽略过程说明。Codex 日志属于内部实现，版本变化可能导致无法捕获；云端或未落盘会话不保证支持。
- Work 暂不支持自动捕获，需手动粘贴。
- 浏览器草稿按回复隔离。清除站点数据会删除草稿，建议定期备份。同一个主机地址与浏览器才能共享原有草稿，`localhost` 和 `127.0.0.1` 的浏览器存储不同。
- 文档预览仅允许服务器所在目录内的文本文件；其他本地文档无法预览。网页链接会打开新标签页。
- 标注位置基于渲染后的文本，Markdown 渲染器升级后可能需要重新定位；项目目前是早期版本。

## 开发和测试

```sh
python3 -m unittest discover -s tests -v
```

核心文件：`server.py`（日志读取及本地 HTTP 服务）、`index.html`（界面和标注）、`manage_service.py`（macOS 服务）。无需构建步骤。

欢迎通过 Issues 报告问题、通过 PR 改进。报告问题时请使用虚构对话复现，不要上传真实会话、令牌或草稿备份。

## License

项目代码使用 MIT License，见 [LICENSE](LICENSE)。内置第三方库及各自许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本项目为独立工具，与 OpenAI 无隶属关系。

## 多工具数据源

默认读取路径（可通过环境变量覆盖，设置后需重启服务）：

| 来源 | 路径 | 环境变量 |
|---|---|---|
| Codex | `~/.codex/sessions`、`archived_sessions` | `CODEX_HOME` |
| Claude Code | `~/.claude/projects/*/*.jsonl` | `CLAUDE_HOME` |
| WorkBuddy | `~/.workbuddy/projects/*/*.jsonl` | `WORKBUDDY_HOME` |

环境变量指向工具的根目录，而不是 projects 目录。Claude Code 解析 assistant.message.content 中的 text，排除 thinking 和工具调用内容；WorkBuddy 解析已完成消息中的 output_text。子代理日志不纳入主会话。会话身份按来源隔离。工具内部日志可能变化，本机已实测 Codex / WorkBuddy；Claude Code 通过虚构格式样例测试，尚未用真实本机会话验证。Claude 普通聊天 / Cowork 不属于此适配范围，可用粘贴导入。

## 筛选与会话迁移

左栏来源筛选支持全部、Codex、WorkBuddy、Claude 和手动导入，会记住选择。展开会话后，进入 **更多 → 复制会话上下文…**，预览并复制按本地记录顺序排列的用户问题与助手文字，交给另一个工具后再补充下一步任务。

此功能导出的是对话正文，不是模型完整运行上下文：不含系统提示、工具原始输出、图片或附件内容。手动导入只能包含已粘贴内容，无法自动取得 GPT / Work 的历史问题。日志已经裁剪、压缩或缺失的内容无法还原。长会话可能超过目标工具输入限制，可在预览框中选择需要的片段复制。
