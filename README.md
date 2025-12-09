# GrowEngine - 广告投放自动化平台

## 🎯 项目简介

GrowEngine 是一个全栈广告投放管理平台，提供：
- 📊 **投放概览**：实时监控消耗、GMV、ROI 等核心指标
- 📋 **计划管理**：广告计划的创建、编辑、启停
- 🤖 **智能诊断**：AI 驱动的投放优化建议
- 🎮 **竞价模拟**：基于 OnlineLp 策略的竞价仿真

## 📁 项目结构

```
ProtoAd/
├── frontend/          # React 前端 (Vite + TailwindCSS)
│   ├── src/
│   │   ├── App.jsx   # 主应用组件
│   │   └── App.css   # 样式文件
│   ├── Dockerfile
│   └── package.json
├── backend/           # Python 后端 (FastAPI)
│   ├── api.py        # API 服务
│   ├── simulator.py  # 竞价模拟器
│   ├── generate_mock_data.py  # 数据生成器
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── scripts/
    └── start-dev.sh  # 开发环境启动脚本
```

## 🚀 快速开始

### 方式一：本地开发（推荐）

**前置条件：**
- Node.js 18+
- Python 3.10+

**启动步骤：**

```bash
# 1. 克隆项目
git clone <repository-url>
cd ProtoAd

# 2. 启动后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python generate_mock_data.py  # 生成测试数据
uvicorn api:app --reload

# 3. 启动前端（新开终端）
cd frontend
npm install
npm run dev
```

**或使用一键脚本：**

```bash
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

**访问地址：**
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 方式二：Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**访问地址：**
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000

## ☁️ 云端部署

### 前端部署 (Vercel)

```bash
cd frontend
npm i -g vercel
vercel
```

### 后端部署 (Railway)

1. 访问 [Railway.app](https://railway.app)
2. 新建项目 → 从 GitHub 导入
3. 选择 `backend` 目录
4. 自动识别 Python 项目并部署

### 其他部署选项

| 服务类型 | 推荐平台 | 说明 |
|---------|---------|------|
| 前端静态 | Vercel / Netlify / Cloudflare Pages | 免费，自动 CI/CD |
| 后端 API | Railway / Render / Fly.io | 有免费额度 |
| 全栈 | Docker + VPS | 自主可控 |

## 📡 API 接口

### 核心接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/api/campaigns` | 获取广告计划列表 |
| POST | `/api/campaigns` | 创建广告计划 |
| PUT | `/api/campaigns/{id}` | 更新广告计划 |
| DELETE | `/api/campaigns/{id}` | 删除广告计划 |
| GET | `/api/metrics/realtime` | 实时指标 |
| GET | `/api/metrics/trend` | 趋势数据 |
| POST | `/api/bidding/simulate` | 竞价模拟 |
| GET | `/api/diagnosis` | 智能诊断 |
| POST | `/api/ai/chat` | AI 对话 |

详细文档请访问: `http://localhost:8000/docs`

## 🛠 技术栈

**前端：**
- React 18
- Vite
- TailwindCSS
- Recharts
- Lucide Icons

**后端：**
- FastAPI
- Uvicorn
- Pandas / NumPy
- Pydantic

## 📝 开发计划

- [x] 投放驾驶舱 1.0
- [x] 计划管理迭代
- [x] 投放创建工作流
- [ ] 竞价后端核心
- [ ] 模型精排服务
- [ ] 竞价仿真模拟器
- [ ] Agentic 自动投放

## 📄 License

MIT License
