"""
点击数据收集器
负责记录用户点击事件并存储到文件
"""
import csv
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from collections import defaultdict

from .config import CLICKS_FILE


class ClickCollector:
    """点击数据收集器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.clicks_file = CLICKS_FILE
        self._file_lock = threading.Lock()
        self._stats_cache: Dict[str, int] = defaultdict(int)
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "ClickCollector":
        """获取单例实例"""
        return cls()

    def record_click(
        self,
        visitor_id: int,
        ad_id: int,
        clicked: int = 1,
        position: int = 0,
        context: Optional[Dict] = None,
        timestamp: Optional[int] = None
    ) -> bool:
        """
        记录点击事件

        Args:
            visitor_id: 访客 ID
            ad_id: 广告 ID
            clicked: 是否点击 (1=点击, 0=曝光)
            position: 展示位置
            context: 上下文信息 (页面、设备等)
            timestamp: 时间戳 (不提供则使用当前时间)

        Returns:
            是否成功记录
        """
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())

        with self._file_lock:
            try:
                # 检查文件是否存在，决定是否写入表头
                file_exists = self.clicks_file.exists()

                with open(self.clicks_file, "a", encoding="utf-8", newline="") as f:
                    fieldnames = ["visitor_id", "ad_id", "clicked", "timestamp", "position", "context"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)

                    if not file_exists:
                        writer.writeheader()

                    writer.writerow({
                        "visitor_id": visitor_id,
                        "ad_id": ad_id,
                        "clicked": clicked,
                        "timestamp": timestamp,
                        "position": position,
                        "context": str(context) if context else ""
                    })

                # 更新统计缓存
                self._stats_cache["total_impressions"] += 1
                if clicked:
                    self._stats_cache["total_clicks"] += 1
                self._stats_cache[f"ad_{ad_id}_impressions"] += 1
                if clicked:
                    self._stats_cache[f"ad_{ad_id}_clicks"] += 1

                return True

            except Exception as e:
                print(f"Error recording click: {e}")
                return False

    def record_impression(
        self,
        visitor_id: int,
        ad_id: int,
        position: int = 0,
        context: Optional[Dict] = None
    ) -> bool:
        """记录曝光事件 (未点击)"""
        return self.record_click(
            visitor_id=visitor_id,
            ad_id=ad_id,
            clicked=0,
            position=position,
            context=context
        )

    def get_stats(self) -> Dict:
        """获取点击统计"""
        total_impressions = self._stats_cache.get("total_impressions", 0)
        total_clicks = self._stats_cache.get("total_clicks", 0)
        ctr = total_clicks / total_impressions if total_impressions > 0 else 0.0

        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "ctr": round(ctr, 4),
            "timestamp": datetime.now().isoformat()
        }

    def get_ad_stats(self, ad_id: int) -> Dict:
        """获取单个广告的点击统计"""
        impressions = self._stats_cache.get(f"ad_{ad_id}_impressions", 0)
        clicks = self._stats_cache.get(f"ad_{ad_id}_clicks", 0)
        ctr = clicks / impressions if impressions > 0 else 0.0

        return {
            "ad_id": ad_id,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 4)
        }

    def load_stats_from_file(self):
        """从文件加载统计数据到缓存"""
        if not self.clicks_file.exists():
            return

        self._stats_cache.clear()

        with open(self.clicks_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ad_id = row["ad_id"]
                clicked = int(row.get("clicked", 1))

                self._stats_cache["total_impressions"] += 1
                if clicked:
                    self._stats_cache["total_clicks"] += 1
                self._stats_cache[f"ad_{ad_id}_impressions"] += 1
                if clicked:
                    self._stats_cache[f"ad_{ad_id}_clicks"] += 1

        print(f"Loaded click stats: {self._stats_cache['total_impressions']} impressions, {self._stats_cache['total_clicks']} clicks")
