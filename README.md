# Dialogue Enhancer · 对话增强器

AI 一次回复很长，你却有好几个地方想追问？选中文字，写下问题或修改意见，一次打包交给 AI。

## 怎么用上？

**把这个 GitHub 链接发给你的 Agent，跟它说「帮我安装并应用这个项目」即可。**

直接复制这句话：

> 帮我在本机安装并应用这个项目：https://github.com/joshuama2002zz-coder/dialogue-enhancer 。完成后打开页面让我使用；如果是 macOS，请帮我设置为登录自动启动。

使用能操作你本地电脑的 Agent，例如 Codex、Claude Code 或 WorkBuddy。具体安装配置交给它处理，你不需要自己敲命令。

## 原理很简单：都在你的电脑上运行

**本地对话记录 → 本地网页阅读和批注 → 本地生成追问 Prompt → 你自行复制回 AI。**

- **没有项目方的云端服务器。** 网页由你电脑上的服务提供，只监听本机地址 `127.0.0.1`。
- **不会主动上传对话。** 读取记录、整理标题和生成 Prompt 都在本地完成，不调用外部模型，也不需要 API key。
- **草稿留在你的浏览器中。** 标注和气泡设置保存在本机浏览器，可以自行备份。
- **由你决定何时交给 AI。** 只有你把内容粘贴并发送给目标 AI 后，这部分内容才交给那个工具处理。

本工具不主动把对话发给项目作者或第三方，但“本地运行”不等于绝对零风险。请保持默认的本机访问方式，不要把服务暴露到公网；你使用的 Agent、浏览器扩展及目标 AI 的数据处理规则仍然适用。

## 打开之后

1. 点击 **Codex / WorkBuddy / Claude** 气泡，找到会话，展开一条回复。
2. **选中文字，直接写意见**，也可以点击预设提问气泡；对整体有建议就点“全文意见”。
3. 点击 **生成追问 Prompt**，选择“重新生成”“解答问题”或“先解答再重新生成”。
4. **复制回同一个 AI 会话**，一次处理所有标注。

支持深色模式、自定义提问气泡和草稿备份。按 **Esc** 可删除最近操作的标注，误删后可点“撤销”。

想换一个 Agent 接着做？展开会话，点击 **更多 → 复制会话上下文**，把问题与回答一起带过去，再告诉它下一步任务。

## 支持哪些工具？

| 工具 | 接入方式 |
|---|---|
| Codex | 自动读取本地会话，已实测 |
| WorkBuddy | 自动读取本地会话，已实测 |
| Claude Code | 已接入日志解析，尚未用真实本机会话验证 |
| ChatGPT / Work / Claude 普通聊天等 | 手动粘贴回复 |

会话迁移仅包含本地可读取的用户和助手文字，不包含系统提示、工具原始输出、图片或附件。手动粘贴的内容不会自动补全原工具里的历史对话。

<details>
<summary>给 Agent / 开发者的安装与维护说明（普通用户无需阅读）</summary>


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


### 数据源


默认读取路径（可通过环境变量覆盖，设置后需重启服务）：

| 来源 | 路径 | 环境变量 |
|---|---|---|
| Codex | `~/.codex/sessions`、`archived_sessions` | `CODEX_HOME` |
| Claude Code | `~/.claude/projects/*/*.jsonl` | `CLAUDE_HOME` |
| WorkBuddy | `~/.workbuddy/projects/*/*.jsonl` | `WORKBUDDY_HOME` |

环境变量指向工具的根目录，而不是 projects 目录。Claude Code 解析 assistant.message.content 中的 text，排除 thinking 和工具调用内容；WorkBuddy 解析已完成消息中的 output_text。子代理日志不纳入主会话。会话身份按来源隔离。工具内部日志可能变化，本机已实测 Codex / WorkBuddy；Claude Code 通过虚构格式样例测试，尚未用真实本机会话验证。Claude 普通聊天 / Cowork 不属于此适配范围，可用粘贴导入。


### 使用边界


- 服务器只监听 `127.0.0.1:8765`，不上传对话、不调用模型、不自动发消息。不要通过公网代理暴露此服务：它没有账户认证，会读取当前用户的本地对话。
- 默认扫描 `~/.codex/sessions` 和 `~/.codex/archived_sessions`，也可通过 `CODEX_HOME` 环境变量指定目录；每 3 秒重新读取。大量历史记录可能影响性能。
- 只读取标记为 `final_answer` / `final` 的 assistant 最终文本，忽略过程说明。Codex 日志属于内部实现，版本变化可能导致无法捕获；云端或未落盘会话不保证支持。
- Work 暂不支持自动捕获，需手动粘贴。
- 浏览器草稿按回复隔离。清除站点数据会删除草稿，建议定期备份。同一个主机地址与浏览器才能共享原有草稿，`localhost` 和 `127.0.0.1` 的浏览器存储不同。
- 文档预览仅允许服务器所在目录内的文本文件；其他本地文档无法预览。网页链接会打开新标签页。
- 标注位置基于渲染后的文本，Markdown 渲染器升级后可能需要重新定位；项目目前是早期版本。


### 测试

```sh
python3 -m unittest discover -s tests -v
```

无需前端构建。核心文件为 `server.py`、`providers.py`、`transcripts.py`、`titles.py`、`index.html` 和 `manage_service.py`。

</details>

## 开源与反馈

欢迎提交 Issues 和 PR。反馈时请使用虚构对话复现，不要上传真实会话、令牌或草稿备份。

项目代码采用 [MIT License](LICENSE)，第三方库许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本项目为独立工具，与 OpenAI 无隶属关系。

## 会话管理

展开会话，在“更多”中可以重命名或删除会话。删除只从增强器中移除，并保存在当前浏览器中，自动同步不会使它重新出现；原工具的日志和可恢复的草稿仍保留。误删可以立即“撤销”，也可以在“设置 → 恢复已删除的会话”中恢复全部。清除浏览器数据会重置删除状态。备份包含自定义标题和删除状态。

手动导入与自动捕获的会话统一按最新消息时间排序，不再固定置顶；导入标题会清理 Markdown 并提取简短主题，也可自行重命名。

## 请我喝一瓶无糖可乐 🥤

如果感觉对你有用，可以赞赏我一瓶无糖可乐。

<p><img src="assets/wechat-support.png" alt="微信赞赏二维码" width="180" /></p>
