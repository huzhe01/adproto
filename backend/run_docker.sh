#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔍 检查 Docker 环境..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误: Docker Desktop 未运行。${NC}"
    echo "请先打开 Docker Desktop 应用程序，等待启动完成后再次运行此脚本。"
    exit 1
fi

echo -e "${GREEN}✅ Docker 正在运行${NC}"

# 构建镜像
echo "📦 正在构建后端镜像 (protoad-backend)..."
docker build -t protoad-backend .
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败${NC}"
    exit 1
fi

# 停止旧容器（如果存在）
if [ "$(docker ps -q -f name=protoad-backend)" ]; then
    echo "🛑 停止旧容器..."
    docker stop protoad-backend
    docker rm protoad-backend
fi

# 运行容器
echo "🚀 启动后端服务..."
# -d: 后台运行
# --rm: 停止后自动删除
# -p 8000:8000: 端口映射
docker run --name protoad-backend -p 8000:8000 --rm -d protoad-backend

echo -e "${GREEN}✨ 部署成功！${NC}"
echo "后端 API 地址: http://localhost:8000"
echo "API 文档地址: http://localhost:8000/docs"
echo ""
echo "查看日志请运行: docker logs -f protoad-backend"
