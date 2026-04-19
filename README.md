# Travel-Agent 旅行智能助手

基于 FastAPI + LangChain + MySQL 构建的 AI 旅行规划系统。用户输入一句话，系统会自动解析需求、查询天气和景点，生成完整的旅行攻略。

## ✨ 功能特性
- 🧠 **AI Agent 自主规划**：LangChain 智能体自动调用工具生成行程
- 🌤️ **实时天气查询**：对接和风天气 API
- 📍 **景点/美食/酒店推荐**：对接高德地图 POI 接口
- 📄 **PDF 导出**：一键生成可打印的旅行计划
- 📚 **历史记录**：MySQL 持久化所有查询和结果
- 🔄 **多轮对话**：支持用户随时调整行程

## 🛠️ 技术栈
- Python 3.10+
- FastAPI
- LangChain
- MySQL
- SQLAlchemy
- ReportLab

## 🚀 快速开始
### 1. 安装依赖
```bash
pip install -r requirements.txt