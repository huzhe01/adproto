#!/usr/bin/env python
"""
NeuralCF 模型训练脚本
基于点击数据训练神经协同过滤模型
"""
import csv
import os
from pathlib import Path

try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_TF = True
except ImportError:
    HAS_TF = False
    print("Warning: tensorflow not installed. Run: pip install tensorflow")

import numpy as np

from ..config import DATA_DIR, MODELS_DIR


def load_training_data():
    """
    加载训练数据

    Returns:
        tuple: (visitor_ids, ad_ids, labels)
    """
    clicks_file = DATA_DIR / "clicks.csv"
    if not clicks_file.exists():
        print(f"Error: {clicks_file} not found")
        return None, None, None

    visitor_ids = []
    ad_ids = []
    labels = []

    with open(clicks_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            visitor_ids.append(int(row["visitor_id"]))
            ad_ids.append(int(row["ad_id"]))
            labels.append(int(row.get("clicked", 1)))

    return (
        np.array(visitor_ids),
        np.array(ad_ids),
        np.array(labels)
    )


def build_neuralcf_model(num_visitors, num_ads, embedding_dim=10):
    """
    构建 NeuralCF 模型

    Args:
        num_visitors: 访客数量
        num_ads: 广告数量
        embedding_dim: 嵌入维度

    Returns:
        keras Model
    """
    if not HAS_TF:
        raise ImportError("tensorflow is required for training")

    # 输入层
    visitor_input = keras.layers.Input(shape=(1,), name="visitor_input")
    ad_input = keras.layers.Input(shape=(1,), name="ad_input")

    # 嵌入层
    visitor_embedding = keras.layers.Embedding(
        num_visitors + 1, embedding_dim, name="visitor_embedding"
    )(visitor_input)
    visitor_vec = keras.layers.Flatten()(visitor_embedding)

    ad_embedding = keras.layers.Embedding(
        num_ads + 1, embedding_dim, name="ad_embedding"
    )(ad_input)
    ad_vec = keras.layers.Flatten()(ad_embedding)

    # 拼接
    concat = keras.layers.Concatenate()([visitor_vec, ad_vec])

    # MLP 层
    x = keras.layers.Dense(64, activation="relu")(concat)
    x = keras.layers.Dropout(0.2)(x)
    x = keras.layers.Dense(32, activation="relu")(x)
    x = keras.layers.Dropout(0.2)(x)

    # 输出层
    output = keras.layers.Dense(1, activation="sigmoid")(x)

    model = keras.Model(inputs=[visitor_input, ad_input], outputs=output)
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")]
    )

    return model


def train_model(model, visitor_ids, ad_ids, labels, epochs=10, batch_size=32):
    """
    训练模型

    Args:
        model: keras Model
        visitor_ids: 访客 ID 数组
        ad_ids: 广告 ID 数组
        labels: 标签数组
        epochs: 训练轮数
        batch_size: 批大小

    Returns:
        训练历史
    """
    # 划分训练/测试集
    split_idx = int(len(labels) * 0.8)
    indices = np.random.permutation(len(labels))

    train_idx = indices[:split_idx]
    test_idx = indices[split_idx:]

    X_train = [visitor_ids[train_idx], ad_ids[train_idx]]
    y_train = labels[train_idx]
    X_test = [visitor_ids[test_idx], ad_ids[test_idx]]
    y_test = labels[test_idx]

    print(f"Training samples: {len(y_train)}")
    print(f"Test samples: {len(y_test)}")

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )

    return history


def save_model(model, output_dir):
    """保存模型为 SavedModel 格式"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存为 SavedModel 格式 (TensorFlow Serving 兼容)
    model.save(output_dir / "neuralcf")
    print(f"Model saved to {output_dir / 'neuralcf'}")


def main():
    """主训练流程"""
    print("=" * 50)
    print("NeuralCF Model Training")
    print("=" * 50)

    # 1. 加载数据
    print("\n1. Loading training data...")
    visitor_ids, ad_ids, labels = load_training_data()

    if visitor_ids is None:
        print("Error: Failed to load training data")
        return

    print(f"   Total samples: {len(labels)}")
    print(f"   Positive samples: {labels.sum()}")
    print(f"   Negative samples: {len(labels) - labels.sum()}")

    # 2. 构建模型
    print("\n2. Building NeuralCF model...")
    num_visitors = visitor_ids.max()
    num_ads = ad_ids.max()
    print(f"   Visitors: {num_visitors}, Ads: {num_ads}")

    try:
        model = build_neuralcf_model(num_visitors, num_ads)
        model.summary()
    except Exception as e:
        print(f"Error building model: {e}")
        return

    # 3. 训练模型
    print("\n3. Training model...")
    try:
        history = train_model(model, visitor_ids, ad_ids, labels, epochs=5)
    except Exception as e:
        print(f"Error training: {e}")
        return

    # 4. 保存模型
    print("\n4. Saving model...")
    save_model(model, MODELS_DIR)

    print("\n" + "=" * 50)
    print("Training completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
