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
#   核心前端: http://localhost:5173/adproto/
#   核心后端: http://localhost:8000
#   推荐前端: http://localhost:5174
#   推荐后端: http://localhost:8001
#

set -euo pipefail

echo "=========================================="
echo "  GrowEngine 开发环境启动脚本"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$HOME/venv/huzhe}"
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

# ==================== Python 设置 ====================
echo -e "\n${BLUE}[2/4] 设置 Python 环境...${NC}"

if [ ! -d "$VENV_DIR" ]; then
    echo "  创建 Python 虚拟环境: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
echo "  安装核心与推荐后端依赖..."
pip install -q -r backend/requirements.txt -r ad_rec_backend/requirements.txt

echo "  生成核心平台测试数据..."
python backend/generate_mock_data.py

# ==================== Node 设置 ====================
echo -e "\n${BLUE}[3/4] 设置前端环境...${NC}"

if [ ! -d "frontend/node_modules" ]; then
    echo "  安装核心前端 npm 依赖..."
    npm install --prefix frontend
fi

if [ ! -d "ad_rec_frontend/node_modules" ]; then
    echo "  安装推荐前端 npm 依赖..."
    npm install --prefix ad_rec_frontend
fi

# ==================== 启动服务 ====================
echo -e "\n${BLUE}[4/4] 启动服务...${NC}"

PIDS=()

echo "  启动核心后端服务 (端口 8000)..."
(cd backend && source "$VENV_DIR/bin/activate" && uvicorn api:app --reload --host 0.0.0.0 --port 8000) &
PIDS+=($!)

echo "  启动推荐后端服务 (端口 8001)..."
(source "$VENV_DIR/bin/activate" && uvicorn ad_rec_backend.api:app --reload --host 0.0.0.0 --port 8001) &
PIDS+=($!)

echo "  启动核心前端服务 (端口 5173)..."
npm run dev --prefix frontend -- --host 0.0.0.0 --port 5173 &
PIDS+=($!)

echo "  启动推荐前端服务 (端口 5174)..."
npm run dev --prefix ad_rec_frontend -- --host 0.0.0.0 --port 5174 &
PIDS+=($!)

sleep 3

echo ""
echo -e "${GREEN}=========================================="
echo "  ✅ GrowEngine 开发环境已启动！"
echo "===========================================${NC}"
echo ""
echo -e "  ${YELLOW}核心前端:${NC} http://localhost:5173/adproto/"
echo -e "  ${YELLOW}核心 API:${NC}  http://localhost:8000/docs"
echo -e "  ${YELLOW}推荐前端:${NC} http://localhost:5174"
echo -e "  ${YELLOW}推荐 API:${NC}  http://localhost:8001/docs"
echo ""
echo -e "  按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo ""

# 捕获退出信号，清理子进程
cleanup() {
    echo ""
    echo "正在停止服务..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    echo "✓ 服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待进程
wait
