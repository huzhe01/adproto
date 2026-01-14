#!/bin/bash
# 广告推荐系统开发启动脚本

echo "=========================================="
echo "  Ad Rec System - Development Server"
echo "=========================================="

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 启动后端
echo -e "${BLUE}Starting backend on port 8001...${NC}"
source ~/venv/huzhe/bin/activate
# 使用完整模块路径，确保相对导入正常工作
uvicorn ad_rec_backend.api:app --reload --port 8001 &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端
echo -e "${BLUE}Starting frontend on port 5174...${NC}"
cd ad_rec_frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}=========================================="
echo "  Services started!"
echo "  Backend:  http://localhost:8001"
echo "  Frontend: http://localhost:5174"
echo "  API Docs: http://localhost:8001/docs"
echo "==========================================${NC}"
echo ""
echo "Press Ctrl+C to stop all services"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
