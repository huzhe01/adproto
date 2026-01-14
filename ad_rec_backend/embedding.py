"""
嵌入向量类
仿 SparrowRecSys 的 Embedding.java
"""
import math
from typing import List, Optional
import numpy as np


class Embedding:
    """嵌入向量类，支持余弦相似度计算"""

    def __init__(self, values: Optional[List[float]] = None):
        """
        初始化嵌入向量

        Args:
            values: 向量值列表，通常为10维
        """
        self.values: List[float] = values or []

    @classmethod
    def from_string(cls, emb_str: str) -> "Embedding":
        """
        从字符串解析嵌入向量
        格式: "0.1 0.2 0.3 ..." 或 "id:0.1 0.2 0.3 ..."

        Args:
            emb_str: 嵌入字符串
        """
        if ":" in emb_str:
            emb_str = emb_str.split(":")[1]

        values = [float(x) for x in emb_str.strip().split()]
        return cls(values)

    def calculate_similarity(self, other: "Embedding") -> float:
        """
        计算与另一个嵌入的余弦相似度

        公式: similarity = (A·B) / (||A|| * ||B||)

        Args:
            other: 另一个嵌入向量

        Returns:
            相似度值，范围 [-1, 1]
        """
        if not self.values or not other.values:
            return 0.0

        if len(self.values) != len(other.values):
            return 0.0

        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0

        for a, b in zip(self.values, other.values):
            dot_product += a * b
            norm_a += a * a
            norm_b += b * b

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (math.sqrt(norm_a) * math.sqrt(norm_b))

    def to_numpy(self) -> np.ndarray:
        """转换为 numpy 数组"""
        return np.array(self.values)

    def __repr__(self) -> str:
        if len(self.values) <= 3:
            return f"Embedding({self.values})"
        return f"Embedding([{self.values[0]:.4f}, {self.values[1]:.4f}, ..., {self.values[-1]:.4f}], dim={len(self.values)})"
