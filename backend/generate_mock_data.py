#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock 数据生成器
===============
生成用于测试的虚拟广告投放数据，包括：
- 广告计划数据
- 竞价流量数据
- 用户行为数据
"""

import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 配置
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
NUM_CAMPAIGNS = 20
NUM_TRAFFIC_RECORDS = 10000
NUM_DAYS = 7

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "traffic"), exist_ok=True)

# ==================== 广告计划生成 ====================

CAMPAIGN_NAMES = [
    "新品推广_冬季大衣", "双11预热_美妆礼盒", "库存清仓_长尾流量",
    "品牌曝光_春节活动", "定向人群_高消费用户", "618大促_数码产品",
    "日常投放_食品饮料", "拉新计划_APP下载", "老客召回_会员专享",
    "测试计划_A/B实验", "爆款打造_热销商品", "内容种草_达人合作",
    "直播引流_预约活动", "搜索广告_关键词投放", "信息流_开屏广告",
    "视频贴片_品牌植入", "社交分享_裂变传播", "私域导流_社群运营",
    "节日营销_礼盒套装", "尾货清仓_限时特惠"
]

BID_TYPES = ["oCPM", "CPC", "CPM", "NOBID"]
STATUSES = ["active", "learning", "paused"]
LEARNING_STAGES = ["passed", "learning", "failed"]
CATEGORIES = ["电商", "游戏", "教育", "金融", "本地生活", "汽车"]


def generate_campaigns(num: int = NUM_CAMPAIGNS) -> List[Dict[str, Any]]:
    """生成广告计划数据"""
    campaigns = []
    
    for i in range(num):
        budget = random.choice([1000, 2000, 3000, 5000, 8000, 10000, 20000])
        bid = random.uniform(10, 150)
        spend_ratio = random.uniform(0.1, 0.95)
        spend = budget * spend_ratio
        
        impressions = int(spend * random.uniform(15, 50))
        clicks = int(impressions * random.uniform(0.01, 0.05))
        conversions = int(clicks * random.uniform(0.01, 0.1))
        
        ctr = clicks / impressions * 100 if impressions > 0 else 0
        cvr = conversions / clicks * 100 if clicks > 0 else 0
        cpa = spend / conversions if conversions > 0 else 0
        
        gmv = conversions * random.uniform(50, 500)
        roi = gmv / spend if spend > 0 else 0
        
        status = random.choice(STATUSES)
        learning_stage = "passed" if status == "active" else random.choice(LEARNING_STAGES)
        if status == "paused":
            learning_stage = random.choice(["passed", "failed"])
        
        campaign = {
            "id": 100 + i,
            "name": f"{random.choice(CAMPAIGN_NAMES)}_V{random.randint(1, 5)}",
            "status": status,
            "budget": budget,
            "bid": round(bid, 2),
            "spend": round(spend, 2),
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "ctr": round(ctr, 2),
            "cvr": round(cvr, 2),
            "cpa": round(cpa, 2),
            "roi": round(roi, 2),
            "gmv": round(gmv, 2),
            "learning_stage": learning_stage,
            "bid_type": random.choice(BID_TYPES),
            "category": random.choice(CATEGORIES),
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        campaigns.append(campaign)
    
    return campaigns


# ==================== 竞价流量生成 ====================

def generate_traffic_data(num_records: int = NUM_TRAFFIC_RECORDS, 
                          advertiser_id: int = 1,
                          period: int = 7) -> pd.DataFrame:
    """
    生成竞价流量数据
    
    字段说明：
    - advertiserNumber: 广告主编号
    - advertiserCategoryIndex: 广告主行业分类索引
    - budget: 日预算
    - CPAConstraint: CPA 约束值
    - timeStepIndex: 时间步索引 (0-47，每天48个时段)
    - pValue: 转化概率预估值
    - leastWinningCost: 历史最低获胜成本
    - conversionAction: 是否产生转化 (0/1)
    """
    
    data = []
    cpa_constraint = random.uniform(50, 200)
    budget = random.choice([5000, 10000, 20000, 50000])
    category_idx = random.randint(0, 5)
    
    for _ in range(num_records):
        time_step = random.randint(0, 47)
        
        # 生成 pValue (转化概率)，通常较小
        p_value = np.random.beta(1, 50)  # beta 分布生成较小的概率值
        
        # 最低获胜成本，与 pValue 相关
        base_cost = cpa_constraint * p_value
        least_winning_cost = base_cost * random.uniform(0.5, 1.5)
        
        # 模拟是否转化
        conversion = 1 if random.random() < p_value else 0
        
        record = {
            "advertiserNumber": advertiser_id,
            "advertiserCategoryIndex": category_idx,
            "budget": budget,
            "CPAConstraint": round(cpa_constraint, 2),
            "timeStepIndex": time_step,
            "pValue": round(p_value, 6),
            "leastWinningCost": round(least_winning_cost, 4),
            "conversionAction": conversion
        }
        data.append(record)
    
    return pd.DataFrame(data)


# ==================== 时序指标生成 ====================

def generate_time_series_metrics(days: int = NUM_DAYS) -> List[Dict[str, Any]]:
    """生成时序指标数据（用于图表展示）"""
    metrics = []
    base_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        for hour in range(24):
            timestamp = base_date + timedelta(days=day, hours=hour)
            
            # 模拟一天内的流量分布
            if 8 <= hour <= 10 or 19 <= hour <= 22:
                # 高峰时段
                base_spend = random.uniform(3000, 6000)
            elif 0 <= hour <= 6:
                # 低谷时段
                base_spend = random.uniform(500, 1500)
            else:
                # 正常时段
                base_spend = random.uniform(1500, 3500)
            
            roi = random.uniform(3.0, 5.5)
            gmv = base_spend * roi
            
            metrics.append({
                "timestamp": timestamp.isoformat(),
                "date": timestamp.strftime("%Y-%m-%d"),
                "hour": hour,
                "time": timestamp.strftime("%H:%M"),
                "spend": round(base_spend, 2),
                "gmv": round(gmv, 2),
                "roi": round(roi, 2),
                "impressions": int(base_spend * random.uniform(20, 50)),
                "clicks": int(base_spend * random.uniform(0.3, 0.8)),
                "conversions": int(base_spend * random.uniform(0.02, 0.08)),
                "ctr": round(random.uniform(2.0, 4.5), 2),
                "cvr": round(random.uniform(1.5, 5.0), 2)
            })
    
    return metrics


# ==================== 主函数 ====================

def main():
    print("=" * 50)
    print("GrowEngine Mock 数据生成器")
    print("=" * 50)
    
    # 1. 生成广告计划数据
    print(f"\n[1/3] 生成 {NUM_CAMPAIGNS} 条广告计划数据...")
    campaigns = generate_campaigns(NUM_CAMPAIGNS)
    campaigns_file = os.path.join(OUTPUT_DIR, "campaigns.json")
    with open(campaigns_file, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)
    print(f"✓ 已保存至: {campaigns_file}")
    
    # 2. 生成竞价流量数据
    print(f"\n[2/3] 生成 {NUM_TRAFFIC_RECORDS} 条竞价流量数据...")
    for period in range(1, 8):  # 生成 7 天的数据
        traffic_df = generate_traffic_data(
            num_records=NUM_TRAFFIC_RECORDS // 7,
            advertiser_id=100 + period,
            period=period
        )
        traffic_file = os.path.join(OUTPUT_DIR, "traffic", f"period-{period}.csv")
        traffic_df.to_csv(traffic_file, index=False)
        print(f"  ✓ Period {period}: {len(traffic_df)} 条记录")
    
    # 3. 生成时序指标数据
    print(f"\n[3/3] 生成 {NUM_DAYS} 天的时序指标数据...")
    metrics = generate_time_series_metrics(NUM_DAYS)
    metrics_file = os.path.join(OUTPUT_DIR, "metrics_timeseries.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"✓ 已保存至: {metrics_file}")
    
    print("\n" + "=" * 50)
    print("✅ 数据生成完成！")
    print(f"   输出目录: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
