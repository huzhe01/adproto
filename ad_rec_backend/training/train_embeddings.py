#!/usr/bin/env python
"""
嵌入训练脚本
基于点击序列训练 Item2Vec 嵌入
"""
import csv
from collections import defaultdict
from pathlib import Path
import random

try:
    from gensim.models import Word2Vec
    HAS_GENSIM = True
except ImportError:
    HAS_GENSIM = False
    print("Warning: gensim not installed. Run: pip install gensim")

from ..config import DATA_DIR, AD_EMBEDDINGS_FILE, VISITOR_EMBEDDINGS_FILE


def load_click_sequences():
    """
    从点击数据加载用户点击序列

    Returns:
        dict: {visitor_id: [ad_id1, ad_id2, ...]}
    """
    clicks_file = DATA_DIR / "clicks.csv"
    if not clicks_file.exists():
        print(f"Error: {clicks_file} not found")
        return {}

    # 按访客分组，按时间排序
    visitor_clicks = defaultdict(list)

    with open(clicks_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 按时间戳排序
    rows.sort(key=lambda x: int(x.get("timestamp", 0)))

    for row in rows:
        visitor_id = row["visitor_id"]
        ad_id = row["ad_id"]
        clicked = int(row.get("clicked", 1))

        # 只使用正例点击
        if clicked == 1:
            visitor_clicks[visitor_id].append(str(ad_id))

    return visitor_clicks


def train_item2vec(sequences, vector_size=10, window=5, min_count=1, epochs=10):
    """
    训练 Item2Vec 模型

    Args:
        sequences: 点击序列列表
        vector_size: 向量维度
        window: 窗口大小
        min_count: 最小出现次数
        epochs: 训练轮数

    Returns:
        Word2Vec model
    """
    if not HAS_GENSIM:
        raise ImportError("gensim is required for training")

    # 过滤空序列
    sequences = [s for s in sequences if len(s) >= 2]

    if not sequences:
        raise ValueError("No valid sequences for training")

    print(f"Training Item2Vec with {len(sequences)} sequences...")

    model = Word2Vec(
        sentences=sequences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=4,
        epochs=epochs
    )

    return model


def save_embeddings(model, output_path):
    """保存嵌入到文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        for ad_id in model.wv.index_to_key:
            vector = model.wv[ad_id]
            vector_str = " ".join([f"{v:.6f}" for v in vector])
            f.write(f"{ad_id}:{vector_str}\n")

    print(f"Saved embeddings to {output_path}")


def compute_visitor_embeddings(ad_embeddings, visitor_clicks):
    """
    计算访客嵌入 (用户点击过的广告嵌入的平均值)

    Args:
        ad_embeddings: {ad_id: [embedding]}
        visitor_clicks: {visitor_id: [ad_id1, ad_id2, ...]}

    Returns:
        {visitor_id: [embedding]}
    """
    visitor_embeddings = {}

    for visitor_id, ad_ids in visitor_clicks.items():
        vectors = []
        for ad_id in ad_ids:
            if ad_id in ad_embeddings:
                vectors.append(ad_embeddings[ad_id])

        if vectors:
            # 取平均
            avg_vector = [sum(v[i] for v in vectors) / len(vectors) for i in range(len(vectors[0]))]
            visitor_embeddings[visitor_id] = avg_vector

    return visitor_embeddings


def main():
    """主训练流程"""
    print("=" * 50)
    print("Item2Vec Embedding Training")
    print("=" * 50)

    # 1. 加载点击序列
    print("\n1. Loading click sequences...")
    visitor_clicks = load_click_sequences()
    print(f"   Loaded {len(visitor_clicks)} visitor sequences")

    # 转换为序列列表
    sequences = list(visitor_clicks.values())

    if not sequences:
        print("Error: No click sequences found")
        return

    # 2. 训练 Item2Vec
    print("\n2. Training Item2Vec...")
    try:
        model = train_item2vec(sequences)
        print(f"   Trained embeddings for {len(model.wv)} ads")
    except Exception as e:
        print(f"Error training: {e}")
        return

    # 3. 保存广告嵌入
    print("\n3. Saving ad embeddings...")
    save_embeddings(model, AD_EMBEDDINGS_FILE)

    # 4. 计算并保存访客嵌入
    print("\n4. Computing visitor embeddings...")
    ad_embeddings = {k: list(model.wv[k]) for k in model.wv.index_to_key}
    visitor_embeddings = compute_visitor_embeddings(ad_embeddings, visitor_clicks)

    with open(VISITOR_EMBEDDINGS_FILE, "w", encoding="utf-8") as f:
        for visitor_id, emb in visitor_embeddings.items():
            vector_str = " ".join([f"{v:.6f}" for v in emb])
            f.write(f"{visitor_id}:{vector_str}\n")

    print(f"   Saved {len(visitor_embeddings)} visitor embeddings")

    print("\n" + "=" * 50)
    print("Training completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
