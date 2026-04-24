# RAG 智能问答与知识库系统

基于 RAG（检索增强生成）架构的企业级智能问答系统，支持多格式文档解析、混合检索、多轮对话、Agent 工具调用，已完成 Docker 容器化部署。

**公网访问地址：http://47.83.204.214**

## 技术栈

- 后端：Python 3.14, FastAPI, LangChain, LangGraph
- 数据库：PostgreSQL 16 + pgvector（向量检索）, Redis（会话/缓存）
- 向量库：Chroma, pgvector
- 前端：Streamlit
- 部署：Docker, docker-compose, Nginx, 阿里云 ECS（香港节点）

## 核心功能

| 功能 | 说明 |
|------|------|
| 文档解析 | 支持 PDF、DOCX、MD、TXT、CSV 多格式 |
| 混合检索 | BM25 + 向量检索 + RRF 融合 |
| Rerank | BGE-reranker 重排序，提升精准度 |
| Agent 工具 | 知识库搜索、计算、时间、天气、股票、翻译、新闻 |
| 多轮对话 | Redis 会话管理 + Query 改写 |
| 流式输出 | SSE 流式响应 |
| 来源追溯 | 答案中自动标注来源 |
| 缓存策略 | Redis 问答缓存，响应时间 3s → 0.1s |

## 快速启动

### 1. 环境要求

Docker 20.10+
Docker Compose 2.0+
Python 3.14（本地开发）

### 2. 配置环境变量

cp .env.example .env
编辑 .env 填写 API Key

### 3. 启动服务

docker-compose up -d

### 4. 访问服务

**本地访问：**
- 前端界面：http://localhost
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

**公网访问（已部署至阿里云 ECS）：**
- 前端界面：http://47.83.204.214
- API 文档：http://47.83.204.214:8000/docs
- 健康检查：http://47.83.204.214:8000/health

## API 接口

| 方法 | 路径                 | 说明         |
|------|--------------------|------------|
| POST | /chat/ask          | 同步问答       |
| POST | /chat/ask/stream   | 流式问答       |
| POST | /agent/chat        | Agent 问答   |
| POST | /agent/chat/stream | Agent 流式问答 |
| POST | /documents/upload  | 上传文档       |
| GET | /health            | 健康检查       |

## 项目结构

hk_rag_project/
├── backend/
│   ├── api/           # 路由层
│   ├── agent/         # Agent 模块（工具、ReAct）
│   ├── retrieval/     # 检索模块（向量库、Rerank）
│   ├── services/      # 业务逻辑
│   └── config/        # 配置文件
├── frontend/          # Streamlit 前端
├── docker/            # Dockerfile
├── nginx/             # Nginx 配置
└── docker-compose.yml

## 部署

### 云部署架构
- 云平台：阿里云 ECS（香港节点）
- 实例规格：2核2G
- 操作系统：Ubuntu 22.04
- 部署方式：Docker 容器化 + Nginx 反向代理
- 安全组：开放 22、80、8000、8501 端口

### 部署步骤
详见 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 测试

# 健康检查
curl http://localhost:8000/health

# 问答测试
curl -X POST http://localhost:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "香港金管局是什么？", "k": 4}'

# 公网测试
curl http://47.83.204.214:8000/health

## 环境变量

| 变量 | 说明 |
|------|------|
| DASHSCOPE_API_KEY | 阿里百炼 API Key |
| OPENAI_API_KEY | OpenAI API Key（可选） |
| POSTGRES_PASSWORD | PostgreSQL 密码 |

## 作者

Pan Qizhan

## 许可

MIT