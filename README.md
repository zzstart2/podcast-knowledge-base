# 答案之书·播客版

> 你的任务不是搜索关键词，而是像一个读过很多书的朋友一样，想想书架上哪一期播客曾经触碰过类似的问题。

一个基于向量搜索的播客知识库。收录中文播客节目，用自然语言提问，找到真正能回应你困惑的那期节目。

**线上地址：** http://47.237.167.8:3000

---

## 技术栈

- **后端**：Python stdlib `http.server`（无框架依赖）
- **数据库**：SQLite（`data/podcast.db`）
- **向量搜索**：MiniMax `embo-01` embedding + NumPy 余弦相似度
- **前端**：单文件 HTML + 原生 JS（`ui/answer-book.html`）
- **部署**：阿里云 ECS + systemd

## 当前数据

收录 5 个播客，约 450 期节目（持续丰富中）：

| 播客 | 主播 | 方向 |
|------|------|------|
| 无人知晓 | 孟岩 | 投资·人生·深度对话 |
| 得意忘形 | 张潇雨 | 思维·投资·生活哲学 |
| 知行小酒馆 | 艾菲 | 个人成长·认知 |
| 山下声 | — | 生活·创作·手艺 |
| 岩中花述 | — | 女性·独立·思考 |

---

## 本地运行

**前置条件**

```bash
pip install -r requirements.txt
# 需要 MINIMAX_API_KEY 用于向量搜索（没有 key 会自动降级为关键词搜索）
```

在项目根目录创建 `.env`：

```
MINIMAX_API_KEY=your_key_here
ADMIN_TOKEN=your_admin_token
```

**启动服务**

```bash
python3 tools/server.py
# 访问 http://localhost:3000
```

---

## 添加新播客

**自动方式**（推荐）：

```bash
python3 tools/add_podcast.py "播客名称" --confirm
```

会自动完成：搜索 Apple Podcasts → 抓取 RSS → AI 丰富内容 → 生成向量 → 导入数据库。

**手动分步**：

```bash
# 1. 抓取 RSS
python3 tools/scrape_rss.py "播客名称"

# 2. AI 丰富（提取摘要、标签、问题匹配）
python3 tools/enrich.py

# 3. 生成向量 embedding
python3 tools/embed.py

# 4. 导入数据库
python3 tools/import_db.py
```

---

## 项目结构

```
tools/
  server.py        # Web 服务器（路由 + 搜索 + Admin API）
  add_podcast.py   # 一键添加播客的完整流程
  scrape_rss.py    # RSS 抓取
  enrich.py        # MiniMax LLM 丰富内容（摘要/标签/问题匹配）
  embed.py         # 生成向量 embedding
  import_db.py     # 导入 SQLite
  search.py        # 搜索辅助工具

ui/
  answer-book.html # 主界面（播客浏览 + 向量搜索）
  admin.html       # 管理后台（播客增删改、任务日志）
  covers/          # 播客封面图（{id}.jpg）

data/
  podcast.db       # SQLite 数据库
  scraped/         # RSS 抓取原始 JSON
  enriched/        # AI 丰富后的 JSON

skill/
  system-prompt.md # "答案之书"人设 prompt
```

---

## 部署（阿里云 ECS）

参见 [DEPLOY.md](DEPLOY.md)。服务以 systemd 运行：

```bash
sudo systemctl status podcast-lib
sudo journalctl -u podcast-lib -f
```
