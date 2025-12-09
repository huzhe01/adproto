#!/bin/bash
# ===========================================
# GrowEngine 本地开发启动脚本
# ===========================================
#
# 使用方法:
#   chmod +x scripts/start-dev.sh
#   ./scripts/start-dev.sh
#
# 服务访问:
#   前端: http://localhost:5173
#   后端: http://localhost:8000
#   API文档: http://localhost:8000/docs
#

set -e

echo "=========================================="
echo "  GrowEngine 开发环境启动脚本"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "\n${BLUE}[1/4] 检查依赖...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装"
    exit 1
fi
echo "✓ Python3: $(python3 --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装"
    exit 1
fi
echo "✓ Node.js: $(node --version)"

# ==================== 后端设置 ====================
echo -e "\n${BLUE}[2/4] 设置后端环境...${NC}"

cd backend

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "  创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "  安装 Python 依赖..."
pip install -q -r requirements.txt

# 生成 Mock 数据
echo "  生成测试数据..."
python generate_mock_data.py

cd "$PROJECT_ROOT"

# ==================== 前端设置 ====================
echo -e "\n${BLUE}[3/4] 设置前端环境...${NC}"

cd frontend

# 安装依赖（如果 node_modules 不存在）
if [ ! -d "node_modules" ]; then
    echo "  安装 npm 依赖..."
    npm install
fi

cd "$PROJECT_ROOT"

# ==================== 启动服务 ====================
echo -e "\n${BLUE}[4/4] 启动服务...${NC}"

# 启动后端（后台运行）
echo "  启动后端服务 (端口 8000)..."
cd backend
source venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd "$PROJECT_ROOT"

# 等待后端启动
sleep 2

# 启动前端
echo "  启动前端服务 (端口 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

cd "$PROJECT_ROOT"

# 等待前端启动
sleep 3

echo ""
echo -e "${GREEN}=========================================="
echo "  ✅ GrowEngine 开发环境已启动！"
echo "===========================================${NC}"
echo ""
echo -e "  ${YELLOW}前端:${NC}     http://localhost:5173"
echo -e "  ${YELLOW}后端 API:${NC} http://localhost:8000"
echo -e "  ${YELLOW}API 文档:${NC} http://localhost:8000/docs"
echo ""
echo -e "  按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo ""

# 捕获退出信号，清理子进程
cleanup() {
    echo ""
    echo "正在停止服务..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✓ 服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待进程
wait
