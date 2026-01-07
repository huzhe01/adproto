#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GrowEngine 后端 API 服务
=========================
提供广告投放平台的核心 API 接口，包括：
- 广告计划 CRUD
- 实时数据监控
- 模拟竞价服务
- AI 诊断建议

技术栈: FastAPI + Uvicorn
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import math
import uuid
import json
import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== 应用初始化 ====================

app = FastAPI(
    title="GrowEngine API",
    description="广告投放自动化平台 - 后端 API 服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class Campaign(BaseModel):
    """广告计划模型"""
    id: int
    name: str
    status: str = "learning"  # active, learning, paused
    budget: float = 5000
    bid: float = 65
    spend: float = 0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0
    cvr: float = 0
    cpa: float = 0
    roi: float = 0
    learning_stage: str = "learning"  # learning, passed, failed
    bid_type: str = "oCPM"  # CPC, CPM, oCPM, NOBID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CampaignCreate(BaseModel):
    """创建广告计划请求"""
    name: str
    budget: float = Field(ge=100, le=1000000)
    bid: float = Field(ge=0.1, le=10000)
    target_type: str = "商品购买"
    bid_type: str = "oCPM"

class CampaignUpdate(BaseModel):
    """更新广告计划请求"""
    name: Optional[str] = None
    budget: Optional[float] = None
    bid: Optional[float] = None
    status: Optional[str] = None

class BidRequest(BaseModel):
    """竞价请求"""
    campaign_id: int
    p_value: float  # 预估转化率
    user_features: Optional[Dict[str, Any]] = None

class BidResponse(BaseModel):
    """竞价响应"""
    bid_price: float
    win_probability: float
    estimated_conversion: float

class DiagnosticItem(BaseModel):
    """诊断项目"""
    type: str  # warning, opportunity, success
    title: str
    description: str
    action: str
    priority: int = 1

class MetricsSnapshot(BaseModel):
    """实时指标快照"""
    timestamp: str
    total_spend: float
    total_gmv: float
    roi: float
    ctr: float
    cvr: float
    active_campaigns: int

class AgentChatRequest(BaseModel):
    """Agent 对话请求"""
    messages: List[Dict[str, str]]
    enable_tools: bool = True

class CampaignPreview(BaseModel):
    """AI 生成的计划预览"""
    name: str
    budget: float
    bid: float
    target_type: str = "商品购买"
    bid_type: str = "oCPM"

# ==================== LLM Agent 配置 ====================

LLM_CONFIG = {
    "api_base": os.getenv("LLM_API_BASE", "https://680728.xyz/v1"),
    "api_key": os.getenv("LLM_API_KEY", ""),
    "model": os.getenv("LLM_MODEL", "qwen-max")
}

AGENT_SYSTEM_PROMPT = """你是 GrowEngine 广告投放平台的智能助手「智投星」。你可以帮助用户：
1. 查询当前广告计划的数据和效果
2. 分析投放问题并给出优化建议
3. 根据用户需求创建新的广告计划

你有以下工具可以使用：
- get_campaigns: 获取当前所有广告计划数据
- get_diagnosis: 获取智能诊断建议
- create_campaign_preview: 创建广告计划预览（用户需确认后才会真正创建）

回答时请：
- 使用中文回复
- 简洁专业，直击要点
- 如果需要创建计划，先调用 create_campaign_preview 生成预览
- 数据展示时使用清晰的格式"""

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_campaigns",
            "description": "获取当前所有广告计划的数据，包括名称、状态、预算、消耗、ROI等指标。当用户询问广告效果、投放数据时调用此工具。"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_diagnosis",
            "description": "获取智能诊断建议，分析当前投放问题和优化机会。当用户询问如何优化、有什么问题时调用此工具。"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_campaign_preview",
            "description": "根据用户需求生成广告计划预览，需要用户确认后才会真正创建。当用户要求创建新计划时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "计划名称，应该包含活动类型和产品信息"
                    },
                    "budget": {
                        "type": "number",
                        "description": "日预算(元)，默认5000"
                    },
                    "bid": {
                        "type": "number",
                        "description": "目标CPA出价(元)，默认65"
                    },
                    "target_type": {
                        "type": "string",
                        "description": "投放目标：商品购买、表单提交、应用下载",
                        "enum": ["商品购买", "表单提交", "应用下载"]
                    },
                    "bid_type": {
                        "type": "string",
                        "description": "出价方式",
                        "enum": ["oCPM", "CPC", "CPM"]
                    }
                },
                "required": ["name", "budget", "bid"]
            }
        }
    }
]

# ==================== 模拟数据存储 (内存) ====================

# 初始化模拟广告计划数据
MOCK_CAMPAIGNS: Dict[int, Campaign] = {}

def init_mock_data():
    """初始化模拟数据"""
    global MOCK_CAMPAIGNS
    
    campaign_data = [
        {
            "id": 101,
            "name": "新品推广_冬季大衣_V1",
            "status": "active",
            "budget": 5000,
            "bid": 45.00,
            "spend": 3200.50,
            "impressions": 85200,
            "clicks": 2130,
            "ctr": 2.50,
            "cvr": 3.2,
            "cpa": 47.06,
            "roi": 3.8,
            "learning_stage": "passed",
            "bid_type": "oCPM"
        },
        {
            "id": 102,
            "name": "双11预热_美妆礼盒_自动出价",
            "status": "learning",
            "budget": 2000,
            "bid": 120.00,
            "spend": 450.00,
            "impressions": 12000,
            "clicks": 180,
            "ctr": 1.50,
            "cvr": 1.1,
            "cpa": 225.00,
            "roi": 0.8,
            "learning_stage": "learning",
            "bid_type": "NOBID"
        },
        {
            "id": 103,
            "name": "库存清仓_长尾流量_003",
            "status": "paused",
            "budget": 1000,
            "bid": 20.00,
            "spend": 890.00,
            "impressions": 150000,
            "clicks": 4500,
            "ctr": 3.00,
            "cvr": 0.5,
            "cpa": 39.55,
            "roi": 1.2,
            "learning_stage": "failed",
            "bid_type": "CPC"
        },
        {
            "id": 104,
            "name": "品牌曝光_春节活动_A/B测试",
            "status": "active",
            "budget": 8000,
            "bid": 80.00,
            "spend": 5600.00,
            "impressions": 220000,
            "clicks": 6600,
            "ctr": 3.00,
            "cvr": 2.8,
            "cpa": 30.27,
            "roi": 4.5,
            "learning_stage": "passed",
            "bid_type": "oCPM"
        },
        {
            "id": 105,
            "name": "定向人群_高消费用户_精准投放",
            "status": "active",
            "budget": 3000,
            "bid": 150.00,
            "spend": 1800.00,
            "impressions": 8000,
            "clicks": 320,
            "ctr": 4.00,
            "cvr": 5.5,
            "cpa": 102.27,
            "roi": 5.2,
            "learning_stage": "passed",
            "bid_type": "oCPM"
        }
    ]
    
    for data in campaign_data:
        now = datetime.now().isoformat()
        campaign = Campaign(**data, created_at=now, updated_at=now)
        MOCK_CAMPAIGNS[campaign.id] = campaign

# 启动时初始化数据
init_mock_data()

# ==================== API 路由 ====================

# ---------- 健康检查 ----------

@app.get("/", tags=["System"])
async def root():
    """API 根路由"""
    return {
        "service": "GrowEngine API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ---------- 广告计划管理 ----------

@app.get("/api/campaigns", response_model=List[Campaign], tags=["Campaigns"])
async def list_campaigns(
    status: Optional[str] = Query(None, description="按状态过滤"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """获取广告计划列表"""
    campaigns = list(MOCK_CAMPAIGNS.values())
    
    if status:
        campaigns = [c for c in campaigns if c.status == status]
    
    return campaigns[offset:offset + limit]

@app.get("/api/campaigns/{campaign_id}", response_model=Campaign, tags=["Campaigns"])
async def get_campaign(campaign_id: int):
    """获取单个广告计划详情"""
    if campaign_id not in MOCK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    return MOCK_CAMPAIGNS[campaign_id]

@app.post("/api/campaigns", response_model=Campaign, tags=["Campaigns"])
async def create_campaign(request: CampaignCreate):
    """创建新广告计划"""
    new_id = max(MOCK_CAMPAIGNS.keys(), default=100) + 1
    now = datetime.now().isoformat()
    
    new_campaign = Campaign(
        id=new_id,
        name=request.name,
        budget=request.budget,
        bid=request.bid,
        bid_type=request.bid_type,
        status="learning",
        learning_stage="learning",
        spend=0,
        impressions=0,
        clicks=0,
        ctr=0,
        cvr=0,
        cpa=0,
        roi=0,
        created_at=now,
        updated_at=now
    )
    
    MOCK_CAMPAIGNS[new_id] = new_campaign
    return new_campaign

@app.put("/api/campaigns/{campaign_id}", response_model=Campaign, tags=["Campaigns"])
async def update_campaign(campaign_id: int, request: CampaignUpdate):
    """更新广告计划"""
    if campaign_id not in MOCK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    campaign = MOCK_CAMPAIGNS[campaign_id]
    update_data = request.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.now().isoformat()
    MOCK_CAMPAIGNS[campaign_id] = campaign
    return campaign

@app.delete("/api/campaigns/{campaign_id}", tags=["Campaigns"])
async def delete_campaign(campaign_id: int):
    """删除广告计划"""
    if campaign_id not in MOCK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    del MOCK_CAMPAIGNS[campaign_id]
    return {"message": f"Campaign {campaign_id} deleted successfully"}

@app.post("/api/campaigns/{campaign_id}/toggle", response_model=Campaign, tags=["Campaigns"])
async def toggle_campaign_status(campaign_id: int):
    """切换广告计划状态 (启用/暂停)"""
    if campaign_id not in MOCK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    campaign = MOCK_CAMPAIGNS[campaign_id]
    
    if campaign.status == "paused":
        campaign.status = "active"
    else:
        campaign.status = "paused"
    
    campaign.updated_at = datetime.now().isoformat()
    return campaign

# ---------- 实时数据 ----------

@app.get("/api/metrics/realtime", response_model=MetricsSnapshot, tags=["Metrics"])
async def get_realtime_metrics():
    """获取实时指标数据"""
    campaigns = list(MOCK_CAMPAIGNS.values())
    active_campaigns = [c for c in campaigns if c.status == "active"]
    
    total_spend = sum(c.spend for c in campaigns)
    total_gmv = sum(c.spend * c.roi for c in campaigns)
    avg_roi = total_gmv / total_spend if total_spend > 0 else 0
    
    # 添加一点随机波动模拟实时数据
    fluctuation = random.uniform(0.98, 1.02)
    
    return MetricsSnapshot(
        timestamp=datetime.now().isoformat(),
        total_spend=round(total_spend * fluctuation, 2),
        total_gmv=round(total_gmv * fluctuation, 2),
        roi=round(avg_roi * fluctuation, 2),
        ctr=round(random.uniform(2.8, 3.5), 2),
        cvr=round(random.uniform(2.0, 4.0), 2),
        active_campaigns=len(active_campaigns)
    )

@app.get("/api/metrics/trend", tags=["Metrics"])
async def get_metrics_trend(
    hours: int = Query(24, ge=1, le=168, description="获取多少小时内的趋势数据")
):
    """获取趋势数据 (用于图表展示)"""
    data = []
    now = datetime.now()
    
    for i in range(hours):
        timestamp = now - timedelta(hours=hours - i)
        
        # 模拟一天内的流量分布 (早高峰、晚高峰)
        hour = timestamp.hour
        if 8 <= hour <= 10 or 19 <= hour <= 22:
            base_spend = random.uniform(3000, 5000)
        elif 0 <= hour <= 6:
            base_spend = random.uniform(500, 1500)
        else:
            base_spend = random.uniform(1500, 3000)
        
        roi = random.uniform(3.5, 5.0)
        
        data.append({
            "time": timestamp.strftime("%H:%M"),
            "date": timestamp.strftime("%Y-%m-%d"),
            "spend": round(base_spend, 2),
            "gmv": round(base_spend * roi, 2),
            "roas": round(roi, 2)
        })
    
    return data

# ---------- 竞价服务 ----------

@app.post("/api/bidding/calculate", response_model=BidResponse, tags=["Bidding"])
async def calculate_bid(request: BidRequest):
    """计算竞价出价"""
    if request.campaign_id not in MOCK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail=f"Campaign {request.campaign_id} not found")
    
    campaign = MOCK_CAMPAIGNS[request.campaign_id]
    
    # 使用 OnlineLp 策略计算出价: bid = alpha * pValue
    # 这里 alpha 约等于 CPA 目标
    alpha = campaign.bid
    bid_price = alpha * request.p_value
    
    # 模拟获胜概率 (基于出价和市场竞争)
    win_probability = min(0.95, 0.3 + bid_price / 200)
    
    # 预估转化
    estimated_conversion = request.p_value * win_probability
    
    return BidResponse(
        bid_price=round(bid_price, 4),
        win_probability=round(win_probability, 4),
        estimated_conversion=round(estimated_conversion, 6)
    )

@app.post("/api/bidding/simulate", tags=["Bidding"])
async def simulate_auction(campaign_id: int, steps: int = Query(48, ge=1, le=100)):
    """模拟竞价过程"""
    if campaign_id not in MOCK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    campaign = MOCK_CAMPAIGNS[campaign_id]
    results = []
    
    total_cost = 0
    total_conversions = 0
    total_wins = 0
    remaining_budget = campaign.budget
    cpa_constraint = campaign.bid * 1.5  # 模拟 CPA 约束
    
    # 模拟 alpha 变化曲线 (先升后降或波动)
    base_alpha = campaign.bid
    
    for step in range(steps):
        # 模拟 Alpha 动态调整
        progress = step / steps
        alpha_factor = 1.0 + 0.3 * math.sin(progress * math.pi * 2) + random.uniform(-0.1, 0.1)
        current_alpha = base_alpha * alpha_factor
        
        # 模拟每个时间步的流量
        # 早高峰(8-10点)和晚高峰(19-22点)流量大
        hour_equiv = (step / steps) * 24
        is_peak = (8 <= hour_equiv <= 10) or (19 <= hour_equiv <= 22)
        traffic_count = random.randint(150, 300) if is_peak else random.randint(50, 120)
        
        step_cost = 0
        step_conversions = 0
        step_wins = 0
        
        for _ in range(traffic_count):
            p_value = random.uniform(0.001, 0.08)
            bid_price = current_alpha * p_value
            
            # 模拟市场竞争价格
            market_price = random.uniform(0.5, bid_price * 1.3)
            
            if bid_price >= market_price:
                # 预算控制
                if step_cost + market_price <= remaining_budget:
                    step_wins += 1
                    step_cost += market_price
                    
                    # 模拟转化
                    if random.random() < p_value:
                        step_conversions += 1
        
        remaining_budget -= step_cost
        total_cost += step_cost
        total_conversions += step_conversions
        total_wins += step_wins
        
        real_cpa = total_cost / max(total_conversions, 1)
        
        results.append({
            "step": step,
            "alpha": round(current_alpha, 2),
            "traffic": traffic_count,
            "wins": step_wins,
            "cost": round(step_cost, 2),
            "conversions": step_conversions,
            "total_cost": round(total_cost, 2),
            "total_wins": total_wins,
            "total_conversions": total_conversions,
            "real_cpa": round(real_cpa, 2),
            "remaining_budget": round(remaining_budget, 2),
            "budget_percentage": round((campaign.budget - remaining_budget) / campaign.budget * 100, 1),
            "roi": round((total_conversions * 150) / max(total_cost, 1), 2)  # 假设客单价 150
        })
    
    return {
        "meta": {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "budget": campaign.budget,
            "cpa_constraint": round(cpa_constraint, 2)
        },
        "history": results
    }

# ---------- AI 诊断服务 ----------

@app.get("/api/diagnosis", response_model=List[DiagnosticItem], tags=["AI Diagnosis"])
async def get_diagnosis():
    """获取智能诊断建议"""
    campaigns = list(MOCK_CAMPAIGNS.values())
    diagnostics = []
    
    for campaign in campaigns:
        # 检测学习失败
        if campaign.learning_stage == "failed":
            diagnostics.append(DiagnosticItem(
                type="warning",
                title=f"计划 [{campaign.name[:15]}...] 学习失败",
                description=f"该计划冷启动失败，当前 CTR {campaign.ctr}% 低于行业均值。建议检查定向人群或提高出价。",
                action="一键优化设置",
                priority=1
            ))
        
        # 检测 ROI 过低
        if campaign.roi < 1.0 and campaign.status == "active":
            diagnostics.append(DiagnosticItem(
                type="warning",
                title=f"计划 [{campaign.name[:15]}...] ROI 低于盈亏线",
                description=f"当前 ROI 仅为 {campaign.roi}，低于 1.0 盈亏平衡点。持续投放将造成亏损。",
                action="暂停计划",
                priority=1
            ))
        
        # 发现高潜力
        if campaign.roi > 4.0 and campaign.spend < campaign.budget * 0.5:
            diagnostics.append(DiagnosticItem(
                type="opportunity",
                title=f"高潜力计划 [{campaign.name[:15]}...]",
                description=f"该计划 ROI 达到 {campaign.roi}，但预算消耗仅 {campaign.spend/campaign.budget*100:.1f}%，存在起量空间。",
                action="提升出价 +15%",
                priority=2
            ))
    
    # 通用建议
    if not diagnostics:
        diagnostics.append(DiagnosticItem(
            type="success",
            title="投放状态良好",
            description="当前所有计划运行正常，暂无异常需要处理。",
            action="查看详细报告",
            priority=3
        ))
    
    return sorted(diagnostics, key=lambda x: x.priority)

# ---------- AI 助手 ----------

@app.post("/api/ai/chat", tags=["AI Assistant"])
async def ai_chat(message: str = Query(..., min_length=1)):
    """AI 助手对话接口"""

    # 简单的关键词匹配响应 (生产环境应接入真正的 LLM)
    responses = {
        "roi": "根据您的投放数据分析，目前计划「新品推广_冬季大衣_V1」表现最佳，ROI达到3.8。建议继续加大预算。",
        "消耗": "近7天整体消耗趋势上升12%，GMV增长24%。投放效率持续优化中。主力消耗计划为「品牌曝光_春节活动」。",
        "学习": "系统检测到您有1条计划正在冷启动中，预计24小时内完成学习期。建议保持当前出价不变。",
        "素材": "检测到素材「Video_003」点击率连续3天下滑，建议更换创意素材或调整投放人群。",
        "出价": "当前建议出价区间为 ¥40-80 (oCPM模式)。系统将根据实时竞争环境自动调整。",
        "人群": "系统发现 [精致妈妈] 人群在同类商品中转化率极高，但在当前投放中占比不足5%。建议添加该定向包。"
    }

    # 匹配关键词
    for keyword, response in responses.items():
        if keyword in message.lower():
            return {"response": response, "source": "keyword_match"}

    # 默认响应
    default_responses = [
        "根据您的描述，我建议您查看「智能诊断」面板获取更详细的分析。",
        "让我帮您分析一下...目前系统运行正常，如需具体指标请告诉我计划名称或 ID。",
        "您好！我可以帮您分析投放效果、调整出价策略、诊断问题。请问具体想了解什么？"
    ]

    return {
        "response": random.choice(default_responses),
        "source": "default"
    }

# ---------- Agent 工具执行 ----------

def execute_tool(tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """执行 Agent 工具调用"""

    if tool_name == "get_campaigns":
        # 获取所有广告计划数据
        campaigns = list(MOCK_CAMPAIGNS.values())
        campaign_list = []
        for c in campaigns:
            campaign_list.append({
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "budget": c.budget,
                "spend": c.spend,
                "roi": c.roi,
                "ctr": c.ctr,
                "cvr": c.cvr,
                "learning_stage": c.learning_stage
            })
        return {
            "success": True,
            "data": campaign_list,
            "count": len(campaign_list)
        }

    elif tool_name == "get_diagnosis":
        # 获取诊断建议
        campaigns = list(MOCK_CAMPAIGNS.values())
        diagnostics = []

        for campaign in campaigns:
            if campaign.learning_stage == "failed":
                diagnostics.append({
                    "type": "warning",
                    "title": f"计划 [{campaign.name[:15]}...] 学习失败",
                    "suggestion": "检查定向人群或提高出价"
                })
            if campaign.roi < 1.0 and campaign.status == "active":
                diagnostics.append({
                    "type": "warning",
                    "title": f"计划 [{campaign.name[:15]}...] ROI 低于盈亏线",
                    "suggestion": "考虑暂停或优化"
                })
            if campaign.roi > 4.0 and campaign.spend < campaign.budget * 0.5:
                diagnostics.append({
                    "type": "opportunity",
                    "title": f"高潜力计划 [{campaign.name[:15]}...]",
                    "suggestion": f"ROI达到{campaign.roi}，建议提升出价抢量"
                })

        return {
            "success": True,
            "data": diagnostics,
            "count": len(diagnostics)
        }

    elif tool_name == "create_campaign_preview":
        # 创建计划预览（不实际创建，返回预览数据）
        args = arguments or {}
        preview = {
            "name": args.get("name", f"新建计划_{datetime.now().strftime('%m%d')}"),
            "budget": args.get("budget", 5000),
            "bid": args.get("bid", 65),
            "target_type": args.get("target_type", "商品购买"),
            "bid_type": args.get("bid_type", "oCPM"),
            "estimated_impressions": int(args.get("budget", 5000) / args.get("bid", 65) * 1000 * 1.5),
            "estimated_conversions": int(args.get("budget", 5000) / args.get("bid", 65) * 0.8)
        }
        return {
            "success": True,
            "type": "campaign_preview",
            "data": preview,
            "message": "计划预览已生成，等待用户确认创建"
        }

    return {"success": False, "error": f"未知工具: {tool_name}"}

# ---------- Agent 对话接口 (流式响应) ----------

@app.post("/api/ai/agent", tags=["AI Agent"])
async def agent_chat(request: AgentChatRequest):
    """
    Agentic AI 对话接口 - 支持 SSE 流式响应和工具调用

    该接口会：
    1. 将用户消息发送给 LLM
    2. 如果 LLM 决定调用工具，执行工具并将结果返回给 LLM
    3. 流式返回 LLM 的最终回复
    """

    async def generate_stream():
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
            messages.extend(request.messages)

            # 调用 LLM API
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 第一次调用 - 可能会返回工具调用
                response = await client.post(
                    f"{LLM_CONFIG['api_base']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_CONFIG['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": LLM_CONFIG["model"],
                        "messages": messages,
                        "tools": AGENT_TOOLS if request.enable_tools else None,
                        "stream": False  # 先非流式获取，检查是否有工具调用
                    }
                )

                if response.status_code != 200:
                    error_msg = f"LLM API 错误: {response.status_code}"
                    yield f"data: {json.dumps({'type': 'error', 'content': error_msg}, ensure_ascii=False)}\n\n"
                    return

                result = response.json()
                choice = result.get("choices", [{}])[0]
                message = choice.get("message", {})

                # 检查是否有工具调用
                tool_calls = message.get("tool_calls", [])

                if tool_calls:
                    # 有工具调用，执行工具
                    messages.append(message)

                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        try:
                            tool_args = json.loads(tool_call["function"].get("arguments", "{}"))
                        except:
                            tool_args = {}

                        # 发送工具调用事件
                        yield f"data: {json.dumps({'type': 'tool_call', 'tool': tool_name, 'arguments': tool_args}, ensure_ascii=False)}\n\n"

                        # 执行工具
                        tool_result = execute_tool(tool_name, tool_args)

                        # 发送工具结果事件
                        yield f"data: {json.dumps({'type': 'tool_result', 'tool': tool_name, 'result': tool_result}, ensure_ascii=False)}\n\n"

                        # 添加工具结果到消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })

                    # 带工具结果再次调用 LLM，流式返回
                    stream_response = await client.post(
                        f"{LLM_CONFIG['api_base']}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {LLM_CONFIG['api_key']}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": LLM_CONFIG["model"],
                            "messages": messages,
                            "stream": True
                        }
                    )

                    # 流式返回内容
                    async for line in stream_response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield f"data: {json.dumps({'type': 'content', 'content': content}, ensure_ascii=False)}\n\n"
                            except:
                                pass
                else:
                    # 没有工具调用，流式返回内容
                    stream_response = await client.post(
                        f"{LLM_CONFIG['api_base']}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {LLM_CONFIG['api_key']}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": LLM_CONFIG["model"],
                            "messages": messages,
                            "stream": True
                        }
                    )

                    async for line in stream_response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield f"data: {json.dumps({'type': 'content', 'content': content}, ensure_ascii=False)}\n\n"
                            except:
                                pass

        except httpx.TimeoutException:
            yield f"data: {json.dumps({'type': 'error', 'content': 'LLM 请求超时，请稍后重试'}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'服务异常: {str(e)}'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ==================== 启动入口 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
