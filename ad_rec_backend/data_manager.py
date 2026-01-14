"""
数据管理器
仿 SparrowRecSys 的 DataManager.java - 单例模式，管理所有内存数据
"""
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import threading

from .config import (
    DATA_DIR, ADS_FILE, VISITORS_FILE, CLICKS_FILE,
    AD_EMBEDDINGS_FILE, VISITOR_EMBEDDINGS_FILE
)
from .embedding import Embedding
from .models_data import Ad, Visitor, Click


class DataManager:
    """
    数据管理器 - 单例模式

    负责:
    - 加载广告、访客、点击数据
    - 加载嵌入向量
    - 提供数据查询接口
    - 维护类别反向索引
    """

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

        self.ad_map: Dict[int, Ad] = {}
        self.visitor_map: Dict[int, Visitor] = {}
        self.category_index: Dict[str, List[Ad]] = defaultdict(list)
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "DataManager":
        """获取单例实例"""
        return cls()

    def load_data(
        self,
        ads_path: Optional[Path] = None,
        visitors_path: Optional[Path] = None,
        clicks_path: Optional[Path] = None,
        ad_emb_path: Optional[Path] = None,
        visitor_emb_path: Optional[Path] = None
    ):
        """
        加载所有数据

        Args:
            ads_path: 广告数据文件路径
            visitors_path: 访客数据文件路径
            clicks_path: 点击数据文件路径
            ad_emb_path: 广告嵌入文件路径
            visitor_emb_path: 访客嵌入文件路径
        """
        ads_path = ads_path or ADS_FILE
        visitors_path = visitors_path or VISITORS_FILE
        clicks_path = clicks_path or CLICKS_FILE
        ad_emb_path = ad_emb_path or AD_EMBEDDINGS_FILE
        visitor_emb_path = visitor_emb_path or VISITOR_EMBEDDINGS_FILE

        # 加载广告数据
        if ads_path.exists():
            self._load_ads(ads_path)
            print(f"Loaded {len(self.ad_map)} ads")

        # 加载访客数据
        if visitors_path.exists():
            self._load_visitors(visitors_path)
            print(f"Loaded {len(self.visitor_map)} visitors")

        # 加载点击数据
        if clicks_path.exists():
            self._load_clicks(clicks_path)
            print(f"Loaded clicks data")

        # 加载嵌入
        if ad_emb_path.exists():
            self._load_ad_embeddings(ad_emb_path)
            print(f"Loaded ad embeddings")

        if visitor_emb_path.exists():
            self._load_visitor_embeddings(visitor_emb_path)
            print(f"Loaded visitor embeddings")

        # 构建类别反向索引
        self._build_category_index()
        print(f"Built category index with {len(self.category_index)} categories")

    def _load_ads(self, path: Path):
        """加载广告数据"""
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ad = Ad(
                    ad_id=int(row["ad_id"]),
                    title=row.get("title", ""),
                    release_year=int(row.get("release_year", 0)),
                    categories=row.get("categories", "").split("|") if row.get("categories") else [],
                    click_count=int(row.get("click_count", 0)),
                    impression_count=int(row.get("impression_count", 0)),
                    ctr=float(row.get("ctr", 0))
                )
                self.ad_map[ad.ad_id] = ad

    def _load_visitors(self, path: Path):
        """加载访客数据"""
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                visitor = Visitor(
                    visitor_id=int(row["visitor_id"]),
                    avg_ctr=float(row.get("avg_ctr", 0)),
                    click_count=int(row.get("click_count", 0)),
                    impression_count=int(row.get("impression_count", 0))
                )
                self.visitor_map[visitor.visitor_id] = visitor

    def _load_clicks(self, path: Path):
        """加载点击数据"""
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                click = Click(
                    ad_id=int(row["ad_id"]),
                    visitor_id=int(row["visitor_id"]),
                    clicked=int(row.get("clicked", 1)),
                    timestamp=int(row.get("timestamp", 0))
                )
                # 关联到广告和访客
                if click.ad_id in self.ad_map:
                    self.ad_map[click.ad_id].clicks.append(click)
                if click.visitor_id in self.visitor_map:
                    self.visitor_map[click.visitor_id].clicks.append(click)

    def _load_ad_embeddings(self, path: Path):
        """加载广告嵌入"""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                try:
                    ad_id_str, emb_str = line.split(":", 1)
                    ad_id = int(ad_id_str)
                    if ad_id in self.ad_map:
                        self.ad_map[ad_id].emb = Embedding.from_string(emb_str)
                except (ValueError, IndexError):
                    continue

    def _load_visitor_embeddings(self, path: Path):
        """加载访客嵌入"""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                try:
                    visitor_id_str, emb_str = line.split(":", 1)
                    visitor_id = int(visitor_id_str)
                    if visitor_id in self.visitor_map:
                        self.visitor_map[visitor_id].emb = Embedding.from_string(emb_str)
                except (ValueError, IndexError):
                    continue

    def _build_category_index(self):
        """构建类别反向索引"""
        self.category_index.clear()
        for ad in self.ad_map.values():
            for category in ad.categories:
                self.category_index[category].append(ad)

        # 每个类别按 CTR 排序
        for category in self.category_index:
            self.category_index[category].sort(key=lambda x: x.ctr, reverse=True)

    # ==================== 查询接口 ====================

    def get_ad_by_id(self, ad_id: int) -> Optional[Ad]:
        """获取广告"""
        return self.ad_map.get(ad_id)

    def get_visitor_by_id(self, visitor_id: int) -> Optional[Visitor]:
        """获取访客"""
        return self.visitor_map.get(visitor_id)

    def get_ads_by_category(self, category: str, size: int = 100) -> List[Ad]:
        """获取某类别的广告 (按 CTR 排序)"""
        ads = self.category_index.get(category, [])
        return ads[:size]

    def get_top_ads(self, size: int = 100, sort_by: str = "ctr") -> List[Ad]:
        """获取 TOP 广告"""
        ads = list(self.ad_map.values())
        if sort_by == "ctr":
            ads.sort(key=lambda x: x.ctr, reverse=True)
        elif sort_by == "clicks":
            ads.sort(key=lambda x: x.click_count, reverse=True)
        elif sort_by == "year":
            ads.sort(key=lambda x: x.release_year, reverse=True)
        return ads[:size]

    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self.category_index.keys())

    def get_all_ads(self) -> List[Ad]:
        """获取所有广告"""
        return list(self.ad_map.values())

    def get_all_visitors(self) -> List[Visitor]:
        """获取所有访客"""
        return list(self.visitor_map.values())
