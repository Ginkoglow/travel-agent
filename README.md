# ✈️ Travel-Agent 旅行智能助手

基于 **FastAPI + LangChain + MySQL** 构建的 AI 旅行规划系统。用户输入一句话，系统自动解析需求、查询实时天气与 POI，并生成详细的个性化旅行攻略。支持终端多轮对话、流式输出与 PDF 导出。

## ✨ 功能亮点

- 🧠 **AI Agent 智能规划**：基于 LangChain 与 LLM 自主调用工具，生成专业行程  
- 🌤️ **实时天气查询**：对接高德地图天气 API，获取目的地准确天气与穿衣建议  
- 📍 **POI 智能推荐**：高德地图 POI 接口提供景点、美食、酒店实时数据  
- 💬 **多轮对话与上下文记忆**：终端内保留完整对话历史，自然理解后续提问  
- ⚡ **流式输出**：攻略逐字输出，交互体验流畅  
- 📄 **PDF 一键导出**：自动生成排版精美的旅行计划 PDF（支持中文）  
- 🗄️ **历史记录持久化**：MySQL 存储所有查询与生成的方案，可随时回溯  
- 🔧 **通用闲聊保留**：不仅限于旅行，LLM 原有对话能力完整保留  

## 🛠️ 技术栈

| 类型 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI + Uvicorn |
| AI 框架 | LangChain + LangChain-OpenAI |
| 数据库 | MySQL 8.0 + SQLAlchemy |
| 第三方接口 | 高德地图（天气、POI） |
| 配置管理 | Pydantic Settings + python-dotenv |
| PDF 生成 | ReportLab |
| 终端交互 | 自研 TerminalBot + 流式回调 |

## 📁 项目结构

travel-agent/
├── agent/ # Agent 核心逻辑、提示词
├── api/ # FastAPI 路由
├── db/ # 数据库连接、DAO、建表 SQL
├── settings/ # 配置管理（环境变量加载）
├── tools/ # 天气、POI、PDF 导出工具
├── outputs/ # 导出的 PDF 文件存放目录
├── main.py # API 服务入口
├── terminal_bot.py # 终端交互机器人入口
├── requirements.txt # 项目依赖
└── .env.example # 环境变量示例


## 🚀 快速开始
### 1️⃣ 克隆仓库
git clone https://github.com/Ginkoglow/travel-agent.git

cd travel-agent

2️⃣ 安装依赖
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

3️⃣ 配置环境变量
复制 .env.example 为 .env，填入你的 API 密钥与数据库信息：
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
LLM_API_KEY=你的智谱AI或OpenAI密钥
LLM_MODEL=GLM-4.5-Air

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=travel_agent

AMAP_API_KEY=你的高德地图API密钥

4️⃣ 初始化数据库

Get-Content .\db\init.sql | mysql -u root -p

5️⃣ 启动服务
启动 API 服务（用于 Web 调用）：
python main.py
访问 http://127.0.0.1:8000/docs 查看交互文档。
启动终端机器人（命令行交互）：
python terminal_bot.py

🎮 使用示例
终端对话
👤 你：我下周末想去杭州玩两天，喜欢自然风光
🤖 Agent：（流式输出详细攻略，包含天气、POI 和每日行程）
📅 出行日期：2026-04-25
📌 天气参考：...
📍 推荐地点：...
💡 提示：输入 'export pdf' 可将本次旅行计划导出为 PDF 文件。

👤 你：后天那边天气怎么样？
🤖 Agent：（结合上下文回答杭州后天天气）

API 调用
curl -X POST "http://127.0.0.1:8000/api/travel/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "帮我规划成都三日游"}'

📌 注意事项
高德地图 API 免费版有每日调用次数限制，请合理使用。
如需使用 OpenAI 官方接口，请将 .env 中的 LLM_BASE_URL 改回 https://api.openai.com/v1。
PDF 导出依赖系统字体（Windows 下自动使用 SimHei），Linux 环境请自行安装中文字体。

🤝 贡献与反馈
欢迎提出 Issue 或 PR，一起让这个小助手更智能！
如果觉得项目对你有帮助，请给个 ⭐ Star 支持一下～
