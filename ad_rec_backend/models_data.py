"""
数据模型类
仿 SparrowRecSys 的 Movie.java, User.java, Rating.java
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from .embedding import Embedding


@dataclass
class Click:
    """点击记录 (对应 Rating)"""
    ad_id: int
    visitor_id: int
    clicked: int = 1  # 1=点击, 0=曝光未点击
    timestamp: int = 0

    @classmethod
    def from_rating(cls, movie_id: int, user_id: int, rating: float, timestamp: int) -> "Click":
        """从 SparrowRecSys 的 Rating 转换"""
        # rating >= 3.5 视为正例点击
        clicked = 1 if rating >= 3.5 else 0
        return cls(
            ad_id=movie_id,
            visitor_id=user_id,
            clicked=clicked,
            timestamp=timestamp
        )


@dataclass(eq=False)
class Ad:
    """广告 (对应 Movie)"""
    ad_id: int
    title: str = ""
    release_year: int = 0
    categories: List[str] = field(default_factory=list)
    click_count: int = 0
    impression_count: int = 0
    ctr: float = 0.0  # 点击率 (对应 averageRating)
    emb: Optional[Embedding] = None
    clicks: List[Click] = field(default_factory=list)
    features: Dict[str, str] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.ad_id)

    def __eq__(self, other):
        if isinstance(other, Ad):
            return self.ad_id == other.ad_id
        return False

    @classmethod
    def from_movie(
        cls,
        movie_id: int,
        title: str,
        genres: str,
        avg_rating: float = 0.0,
        rating_count: int = 0
    ) -> "Ad":
        """从 SparrowRecSys 的 Movie 数据转换"""
        # 解析发布年份 (格式: "Title (1999)")
        release_year = 0
        if "(" in title and title.endswith(")"):
            try:
                year_str = title[title.rfind("(") + 1:title.rfind(")")]
                release_year = int(year_str)
            except ValueError:
                pass

        # 解析类别 (格式: "Action|Adventure|Sci-Fi")
        categories = genres.split("|") if genres else []

        return cls(
            ad_id=movie_id,
            title=title,
            release_year=release_year,
            categories=categories,
            click_count=rating_count,
            impression_count=int(rating_count / max(avg_rating / 5.0, 0.1)) if avg_rating > 0 else rating_count * 5,
            ctr=avg_rating / 5.0 if avg_rating > 0 else 0.0  # 归一化到 0-1
        )

    def to_dict(self) -> dict:
        """转换为字典 (用于 JSON 序列化)"""
        return {
            "ad_id": self.ad_id,
            "title": self.title,
            "release_year": self.release_year,
            "categories": self.categories,
            "click_count": self.click_count,
            "impression_count": self.impression_count,
            "ctr": round(self.ctr, 4)
        }


@dataclass
class Visitor:
    """访客 (对应 User)"""
    visitor_id: int
    avg_ctr: float = 0.0  # 平均点击率 (对应 averageRating)
    click_count: int = 0
    impression_count: int = 0
    emb: Optional[Embedding] = None
    clicks: List[Click] = field(default_factory=list)
    features: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_user(
        cls,
        user_id: int,
        avg_rating: float = 0.0,
        rating_count: int = 0
    ) -> "Visitor":
        """从 SparrowRecSys 的 User 数据转换"""
        return cls(
            visitor_id=user_id,
            avg_ctr=avg_rating / 5.0 if avg_rating > 0 else 0.0,
            click_count=rating_count,
            impression_count=rating_count * 3  # 假设平均曝光3次产生1次点击
        )

    def to_dict(self) -> dict:
        """转换为字典 (用于 JSON 序列化)"""
        return {
            "visitor_id": self.visitor_id,
            "avg_ctr": round(self.avg_ctr, 4),
            "click_count": self.click_count,
            "impression_count": self.impression_count
        }
