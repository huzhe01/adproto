"""
推荐处理逻辑
仿 SparrowRecSys 的 RecForYouProcess.java 和 SimilarMovieProcess.java
"""
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from .data_manager import DataManager
from .models_data import Ad, Visitor
from .config import CANDIDATE_SIZE, DEFAULT_REC_SIZE


class RecForYouProcess:
    """个性化推荐处理器"""

    @staticmethod
    def get_rec_list(
        visitor_id: int,
        size: int = DEFAULT_REC_SIZE,
        model: str = "emb"
    ) -> List[Ad]:
        """
        获取个性化推荐列表

        流程:
        1. 获取访客对象
        2. 候选生成 (TOP N 广告)
        3. 排序 (基于模型)
        4. 返回 TOP-K

        Args:
            visitor_id: 访客 ID
            size: 返回数量
            model: 排序模型 ("emb", "neuralcf", "default")

        Returns:
            推荐广告列表
        """
        dm = DataManager.get_instance()
        visitor = dm.get_visitor_by_id(visitor_id)

        if not visitor:
            # 访客不存在，返回热门广告
            return dm.get_top_ads(size, sort_by="ctr")

        # 候选生成
        candidates = RecForYouProcess._candidate_generator()

        # 排序
        ranked = RecForYouProcess._ranker(visitor, candidates, model)

        return ranked[:size]

    @staticmethod
    def _candidate_generator() -> List[Ad]:
        """候选生成 - 返回 CTR 最高的广告"""
        dm = DataManager.get_instance()
        return dm.get_top_ads(CANDIDATE_SIZE, sort_by="ctr")

    @staticmethod
    def _ranker(
        visitor: Visitor,
        candidates: List[Ad],
        model: str = "emb"
    ) -> List[Ad]:
        """
        候选排序

        Args:
            visitor: 访客对象
            candidates: 候选广告列表
            model: 排序模型

        Returns:
            排序后的广告列表
        """
        score_map: Dict[Ad, float] = {}

        if model == "emb":
            # 基于嵌入相似度排序
            if visitor.emb is None:
                # 没有嵌入，按 CTR 排序
                return sorted(candidates, key=lambda x: x.ctr, reverse=True)

            for ad in candidates:
                if ad.emb is not None:
                    similarity = visitor.emb.calculate_similarity(ad.emb)
                    score_map[ad] = similarity
                else:
                    score_map[ad] = 0.0

        elif model == "neuralcf":
            # TODO: 调用 TensorFlow Serving
            # 暂时使用嵌入相似度
            return RecForYouProcess._ranker(visitor, candidates, "emb")

        else:
            # 默认: 按候选顺序 (CTR)
            for i, ad in enumerate(candidates):
                score_map[ad] = len(candidates) - i

        # 按分数排序
        sorted_ads = sorted(score_map.keys(), key=lambda x: score_map[x], reverse=True)
        return sorted_ads


class SimilarAdProcess:
    """相似广告推荐处理器"""

    @staticmethod
    def get_rec_list(
        ad_id: int,
        size: int = DEFAULT_REC_SIZE,
        model: str = "emb"
    ) -> List[Ad]:
        """
        获取相似广告列表

        流程:
        1. 获取目标广告
        2. 候选生成 (同类别广告)
        3. 排序 (基于相似度)
        4. 返回 TOP-K

        Args:
            ad_id: 广告 ID
            size: 返回数量
            model: 排序模型

        Returns:
            相似广告列表
        """
        dm = DataManager.get_instance()
        target_ad = dm.get_ad_by_id(ad_id)

        if not target_ad:
            return []

        # 候选生成
        candidates = SimilarAdProcess._candidate_generator(target_ad)

        # 排序
        ranked = SimilarAdProcess._ranker(target_ad, candidates, model)

        return ranked[:size]

    @staticmethod
    def _candidate_generator(target_ad: Ad) -> List[Ad]:
        """
        候选生成 - 基于类别

        从目标广告的所有类别中获取相关广告
        """
        dm = DataManager.get_instance()
        candidates_set = set()

        for category in target_ad.categories:
            category_ads = dm.get_ads_by_category(category, 100)
            for ad in category_ads:
                if ad.ad_id != target_ad.ad_id:
                    candidates_set.add(ad)

        return list(candidates_set)

    @staticmethod
    def _ranker(
        target_ad: Ad,
        candidates: List[Ad],
        model: str = "emb"
    ) -> List[Ad]:
        """
        候选排序

        Args:
            target_ad: 目标广告
            candidates: 候选广告列表
            model: 排序模型

        Returns:
            排序后的广告列表
        """
        score_map: Dict[Ad, float] = {}

        if model == "emb":
            # 基于嵌入相似度排序
            if target_ad.emb is None:
                # 没有嵌入，使用类别相似度 + CTR
                return SimilarAdProcess._ranker(target_ad, candidates, "default")

            for ad in candidates:
                if ad.emb is not None:
                    similarity = target_ad.emb.calculate_similarity(ad.emb)
                    score_map[ad] = similarity
                else:
                    score_map[ad] = 0.0

        else:
            # 默认: 类别相似度 * 0.7 + CTR * 0.3
            target_categories = set(target_ad.categories)

            for ad in candidates:
                ad_categories = set(ad.categories)
                # Jaccard 相似度
                intersection = len(target_categories & ad_categories)
                union = len(target_categories | ad_categories)
                category_sim = intersection / union if union > 0 else 0.0

                score = 0.7 * category_sim + 0.3 * ad.ctr
                score_map[ad] = score

        # 按分数排序
        sorted_ads = sorted(score_map.keys(), key=lambda x: score_map[x], reverse=True)
        return sorted_ads
