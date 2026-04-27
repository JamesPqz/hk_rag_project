# RAG 智能问答系统部署文档

## 一、架构说明

### 1.1 技术栈
- 后端：FastAPI + LangChain + LangGraph
- 数据库：PostgreSQL 16 + pgvector
- 缓存：Redis 7
- 前端：Streamlit
- 反向代理：Nginx
- 容器化：Docker + docker-compose
- 云平台：阿里云 ECS

### 1.2 服务组成
| 服务 | 端口 | 用途 |
|------|------|------|
| Nginx | 80 | 反向代理，统一入口 |
| Backend | 8000 | FastAPI 后端服务 |
| Frontend | 8501 | Streamlit 前端界面 |
| PostgreSQL | 5432 | 数据存储 + 向量检索 |
| Redis | 6379 | 会话缓存 + 问答缓存 |

## 二、环境准备

### 2.1 创建 ECS 实例
- 规格：2核2G
- 系统：Ubuntu 22.04
- 地域：香港

### 2.2 安全组配置
| 端口 | 用途 | 授权对象 |
|------|------|----------|
| 22 | SSH | 0.0.0.0/0 |
| 80 | HTTP | 0.0.0.0/0 |
| 8000 | API | 0.0.0.0/0 |
| 8501 | Streamlit | 0.0.0.0/0 |

## 三、部署步骤

### 3.1 连接服务器
\`\`\`bash
ssh root@47.83.204.214
\`\`\`

### 3.2 安装 Docker
\`\`\`bash
curl -fsSL https://get.docker.com | bash
systemctl start docker
systemctl enable docker
\`\`\`

### 3.3 上传项目代码
\`\`\`bash
# 本地打包
tar --exclude='.venv' --exclude='__pycache__' -czf rag.tar.gz .
scp rag.tar.gz root@47.83.204.214:/root/

# 服务器解压
cd /root
tar -xzf rag.tar.gz
\`\`\`

### 3.4 配置环境变量
\`\`\`bash
cat > .env << 'EOF'
DASHSCOPE_API_KEY=sk-xxxxx
POSTGRES_PASSWORD=postgres123
EOF
\`\`\`

### 3.5 修改 requirements.txt（使用 CPU 版 PyTorch）
\`\`\`txt
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.11.0
\`\`\`

### 3.6 构建并启动服务
\`\`\`bash
docker compose build --no-cache
docker compose up -d
\`\`\`

## 四、验证

### 4.1 健康检查
\`\`\`bash
curl http://localhost:8000/health
\`\`\`

### 4.2 问答测试
\`\`\`bash
curl -X POST http://localhost:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "香港金管局是什么？", "k": 4}'
\`\`\`

### 4.3 公网访问
- 前端：`http://47.83.204.214`
- API 文档：`http://47.83.204.214:8000/docs`

## 五、常用命令

\`\`\`bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 进入容器
docker compose exec backend /bin/bash
\`\`\`