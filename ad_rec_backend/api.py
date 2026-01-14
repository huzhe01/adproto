#!/usr/bin/env python
"""
广告推荐系统 API
基于 FastAPI 实现，仿 SparrowRecSys 的 HTTP 服务
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import uvicorn

from .data_manager import DataManager
from .rec_process import RecForYouProcess, SimilarAdProcess
from .click_collector import ClickCollector
from .config import DEFAULT_REC_SIZE


# ==================== 数据模型 ====================

class AdResponse(BaseModel):
    """广告响应"""
    ad_id: int
    title: str
    release_year: int
    categories: List[str]
    click_count: int
    impression_count: int
    ctr: float


class VisitorResponse(BaseModel):
    """访客响应"""
    visitor_id: int
    avg_ctr: float
    click_count: int
    impression_count: int


class ClickRequest(BaseModel):
    """点击请求"""
    visitor_id: int
    ad_id: int
    clicked: int = 1
    position: int = 0
    context: Optional[Dict[str, Any]] = None


class ClickResponse(BaseModel):
    """点击响应"""
    success: bool
    message: str


class StatsResponse(BaseModel):
    """统计响应"""
    total_impressions: int
    total_clicks: int
    ctr: float
    timestamp: str


# ==================== 应用初始化 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载数据
    print("Loading data...")
    dm = DataManager.get_instance()
    dm.load_data()

    # 加载点击统计
    cc = ClickCollector.get_instance()
    cc.load_stats_from_file()

    print("Ad Rec Backend started!")
    yield
    # 关闭时清理
    print("Ad Rec Backend shutdown")


app = FastAPI(
    title="Ad Rec API",
    description="广告推荐系统 API - 基于 SparrowRecSys",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Ad Rec API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    dm = DataManager.get_instance()
    return {
        "status": "healthy",
        "ads_count": len(dm.ad_map),
        "visitors_count": len(dm.visitor_map),
        "categories_count": len(dm.category_index)
    }


# ==================== 广告端点 ====================

@app.get("/api/rec/ad/{ad_id}", response_model=AdResponse)
async def get_ad(ad_id: int):
    """获取广告详情"""
    dm = DataManager.get_instance()
    ad = dm.get_ad_by_id(ad_id)

    if not ad:
        raise HTTPException(status_code=404, detail=f"Ad {ad_id} not found")

    return AdResponse(
        ad_id=ad.ad_id,
        title=ad.title,
        release_year=ad.release_year,
        categories=ad.categories,
        click_count=ad.click_count,
        impression_count=ad.impression_count,
        ctr=ad.ctr
    )


@app.get("/api/rec/ads", response_model=List[AdResponse])
async def get_recommended_ads(
    visitor_id: int = Query(..., description="访客 ID"),
    size: int = Query(DEFAULT_REC_SIZE, ge=1, le=100, description="返回数量"),
    model: str = Query("emb", description="排序模型: emb, neuralcf, default")
):
    """
    获取个性化推荐广告

    - visitor_id: 访客 ID
    - size: 返回数量 (1-100)
    - model: 排序模型
    """
    ads = RecForYouProcess.get_rec_list(visitor_id, size, model)

    return [
        AdResponse(
            ad_id=ad.ad_id,
            title=ad.title,
            release_year=ad.release_year,
            categories=ad.categories,
            click_count=ad.click_count,
            impression_count=ad.impression_count,
            ctr=ad.ctr
        )
        for ad in ads
    ]


@app.get("/api/rec/similar", response_model=List[AdResponse])
async def get_similar_ads(
    ad_id: int = Query(..., description="广告 ID"),
    size: int = Query(DEFAULT_REC_SIZE, ge=1, le=100, description="返回数量"),
    model: str = Query("emb", description="排序模型: emb, default")
):
    """
    获取相似广告

    - ad_id: 目标广告 ID
    - size: 返回数量 (1-100)
    - model: 排序模型
    """
    ads = SimilarAdProcess.get_rec_list(ad_id, size, model)

    return [
        AdResponse(
            ad_id=ad.ad_id,
            title=ad.title,
            release_year=ad.release_year,
            categories=ad.categories,
            click_count=ad.click_count,
            impression_count=ad.impression_count,
            ctr=ad.ctr
        )
        for ad in ads
    ]


@app.get("/api/rec/top", response_model=List[AdResponse])
async def get_top_ads(
    size: int = Query(DEFAULT_REC_SIZE, ge=1, le=100, description="返回数量"),
    sort_by: str = Query("ctr", description="排序方式: ctr, clicks, year")
):
    """获取热门广告"""
    dm = DataManager.get_instance()
    ads = dm.get_top_ads(size, sort_by)

    return [
        AdResponse(
            ad_id=ad.ad_id,
            title=ad.title,
            release_year=ad.release_year,
            categories=ad.categories,
            click_count=ad.click_count,
            impression_count=ad.impression_count,
            ctr=ad.ctr
        )
        for ad in ads
    ]


@app.get("/api/rec/categories")
async def get_categories():
    """获取所有广告类别"""
    dm = DataManager.get_instance()
    categories = dm.get_all_categories()
    return {"categories": categories, "count": len(categories)}


# ==================== 访客端点 ====================

@app.get("/api/rec/visitor/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: int):
    """获取访客详情"""
    dm = DataManager.get_instance()
    visitor = dm.get_visitor_by_id(visitor_id)

    if not visitor:
        raise HTTPException(status_code=404, detail=f"Visitor {visitor_id} not found")

    return VisitorResponse(
        visitor_id=visitor.visitor_id,
        avg_ctr=visitor.avg_ctr,
        click_count=visitor.click_count,
        impression_count=visitor.impression_count
    )


@app.get("/api/rec/visitors")
async def get_visitors(
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """获取访客列表"""
    dm = DataManager.get_instance()
    visitors = dm.get_all_visitors()[:limit]

    return [
        VisitorResponse(
            visitor_id=v.visitor_id,
            avg_ctr=v.avg_ctr,
            click_count=v.click_count,
            impression_count=v.impression_count
        )
        for v in visitors
    ]


# ==================== 点击端点 ====================

@app.post("/api/rec/click", response_model=ClickResponse)
async def record_click(request: ClickRequest):
    """
    记录点击事件

    - visitor_id: 访客 ID
    - ad_id: 广告 ID
    - clicked: 是否点击 (1=点击, 0=曝光)
    - position: 展示位置
    - context: 上下文信息
    """
    cc = ClickCollector.get_instance()
    success = cc.record_click(
        visitor_id=request.visitor_id,
        ad_id=request.ad_id,
        clicked=request.clicked,
        position=request.position,
        context=request.context
    )

    if success:
        return ClickResponse(success=True, message="Click recorded")
    else:
        raise HTTPException(status_code=500, detail="Failed to record click")


@app.get("/api/rec/stats", response_model=StatsResponse)
async def get_stats():
    """获取点击统计"""
    cc = ClickCollector.get_instance()
    stats = cc.get_stats()

    return StatsResponse(
        total_impressions=stats["total_impressions"],
        total_clicks=stats["total_clicks"],
        ctr=stats["ctr"],
        timestamp=stats["timestamp"]
    )


@app.get("/api/rec/stats/{ad_id}")
async def get_ad_stats(ad_id: int):
    """获取单个广告的点击统计"""
    cc = ClickCollector.get_instance()
    return cc.get_ad_stats(ad_id)


# ==================== 训练端点 ====================

@app.post("/api/rec/train")
async def trigger_training():
    """触发模型训练 (TODO: 实现)"""
    return {
        "status": "pending",
        "message": "Model training not implemented yet"
    }


# ==================== 主入口 ====================

def main():
    """启动服务"""
    uvicorn.run(
        "ad_rec_backend.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )


if __name__ == "__main__":
    main()
