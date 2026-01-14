#!/usr/bin/env python
"""
数据转换脚本
将 SparrowRecSys 的电影数据转换为广告系统数据

转换映射:
- movies.csv → ads.csv
- ratings.csv → clicks.csv (rating >= 3.5 视为点击)
- item2vecEmb.csv → ad_embeddings.csv
- userEmb.csv → visitor_embeddings.csv
"""
import csv
import os
from pathlib import Path
from collections import defaultdict
import shutil


# SparrowRecSys 数据路径
SPARROW_DATA_DIR = Path(__file__).parent.parent.parent / "SparrowRecSys" / "src" / "main" / "resources" / "webroot"
SPARROW_SAMPLE_DIR = SPARROW_DATA_DIR / "sampledata"
SPARROW_MODEL_DIR = SPARROW_DATA_DIR / "modeldata"

# 输出路径
OUTPUT_DIR = Path(__file__).parent / "data"


def convert_movies_to_ads():
    """转换 movies.csv → ads.csv"""
    movies_path = SPARROW_SAMPLE_DIR / "movies.csv"
    ratings_path = SPARROW_SAMPLE_DIR / "ratings.csv"
    output_path = OUTPUT_DIR / "ads.csv"

    if not movies_path.exists():
        print(f"Error: {movies_path} not found")
        return

    # 先统计每部电影的评分数据
    movie_stats = defaultdict(lambda: {"count": 0, "sum": 0.0})
    if ratings_path.exists():
        with open(ratings_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = int(row["movieId"])
                rating = float(row["rating"])
                movie_stats[movie_id]["count"] += 1
                movie_stats[movie_id]["sum"] += rating

    # 转换电影数据
    with open(movies_path, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)

        with open(output_path, "w", encoding="utf-8", newline="") as fout:
            fieldnames = ["ad_id", "title", "release_year", "categories", "click_count", "impression_count", "ctr"]
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                movie_id = int(row["movieId"])
                title = row["title"]
                genres = row["genres"]

                # 解析发布年份
                release_year = 0
                if "(" in title and title.endswith(")"):
                    try:
                        year_str = title[title.rfind("(") + 1:title.rfind(")")]
                        release_year = int(year_str)
                    except ValueError:
                        pass

                # 计算统计数据
                stats = movie_stats[movie_id]
                count = stats["count"]
                avg_rating = stats["sum"] / count if count > 0 else 0.0
                ctr = avg_rating / 5.0  # 归一化到 0-1

                # 估算曝光数 (假设 CTR 约 20%)
                impression_count = int(count / max(ctr, 0.1)) if ctr > 0 else count * 5

                writer.writerow({
                    "ad_id": movie_id,
                    "title": title,
                    "release_year": release_year,
                    "categories": genres,
                    "click_count": count,
                    "impression_count": impression_count,
                    "ctr": round(ctr, 4)
                })

    print(f"Converted movies → ads: {output_path}")


def convert_ratings_to_clicks():
    """转换 ratings.csv → clicks.csv"""
    ratings_path = SPARROW_SAMPLE_DIR / "ratings.csv"
    output_path = OUTPUT_DIR / "clicks.csv"

    if not ratings_path.exists():
        print(f"Error: {ratings_path} not found")
        return

    with open(ratings_path, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)

        with open(output_path, "w", encoding="utf-8", newline="") as fout:
            fieldnames = ["visitor_id", "ad_id", "clicked", "timestamp"]
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                user_id = int(row["userId"])
                movie_id = int(row["movieId"])
                rating = float(row["rating"])
                timestamp = int(row["timestamp"])

                # rating >= 3.5 视为点击
                clicked = 1 if rating >= 3.5 else 0

                writer.writerow({
                    "visitor_id": user_id,
                    "ad_id": movie_id,
                    "clicked": clicked,
                    "timestamp": timestamp
                })

    print(f"Converted ratings → clicks: {output_path}")


def generate_visitors():
    """从点击数据生成访客数据"""
    clicks_path = OUTPUT_DIR / "clicks.csv"
    output_path = OUTPUT_DIR / "visitors.csv"

    if not clicks_path.exists():
        print(f"Error: {clicks_path} not found")
        return

    # 统计每个访客的数据
    visitor_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0})

    with open(clicks_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            visitor_id = int(row["visitor_id"])
            clicked = int(row["clicked"])
            visitor_stats[visitor_id]["impressions"] += 1
            visitor_stats[visitor_id]["clicks"] += clicked

    # 写入访客数据
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["visitor_id", "avg_ctr", "click_count", "impression_count"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for visitor_id, stats in visitor_stats.items():
            clicks = stats["clicks"]
            impressions = stats["impressions"]
            avg_ctr = clicks / impressions if impressions > 0 else 0.0

            writer.writerow({
                "visitor_id": visitor_id,
                "avg_ctr": round(avg_ctr, 4),
                "click_count": clicks,
                "impression_count": impressions
            })

    print(f"Generated visitors: {output_path}")


def convert_embeddings():
    """转换嵌入文件"""
    # 广告嵌入 (item2vecEmb.csv → ad_embeddings.csv)
    item_emb_path = SPARROW_MODEL_DIR / "item2vecEmb.csv"
    ad_emb_output = OUTPUT_DIR / "ad_embeddings.csv"

    if item_emb_path.exists():
        shutil.copy(item_emb_path, ad_emb_output)
        print(f"Copied item embeddings → ad embeddings: {ad_emb_output}")
    else:
        print(f"Warning: {item_emb_path} not found")

    # 访客嵌入 (userEmb.csv → visitor_embeddings.csv)
    user_emb_path = SPARROW_MODEL_DIR / "userEmb.csv"
    visitor_emb_output = OUTPUT_DIR / "visitor_embeddings.csv"

    if user_emb_path.exists():
        shutil.copy(user_emb_path, visitor_emb_output)
        print(f"Copied user embeddings → visitor embeddings: {visitor_emb_output}")
    else:
        print(f"Warning: {user_emb_path} not found")


def main():
    """执行所有转换"""
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("SparrowRecSys → Ad Rec System 数据转换")
    print("=" * 50)
    print(f"Source: {SPARROW_DATA_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 50)

    # 1. 转换电影 → 广告
    convert_movies_to_ads()

    # 2. 转换评分 → 点击
    convert_ratings_to_clicks()

    # 3. 生成访客数据
    generate_visitors()

    # 4. 转换嵌入
    convert_embeddings()

    print("=" * 50)
    print("转换完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
