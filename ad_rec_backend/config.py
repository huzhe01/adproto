"""
配置文件
"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# 数据文件路径
ADS_FILE = DATA_DIR / "ads.csv"
VISITORS_FILE = DATA_DIR / "visitors.csv"
CLICKS_FILE = DATA_DIR / "clicks.csv"
AD_EMBEDDINGS_FILE = DATA_DIR / "ad_embeddings.csv"
VISITOR_EMBEDDINGS_FILE = DATA_DIR / "visitor_embeddings.csv"

# 推荐配置
CANDIDATE_SIZE = 800  # 候选池大小
DEFAULT_REC_SIZE = 10  # 默认推荐数量
EMBEDDING_DIM = 10  # 嵌入维度

# 数据源配置
EMB_DATA_SOURCE = os.getenv("EMB_DATA_SOURCE", "file")  # "file" or "redis"

# 外部服务
JAVA_REC_SERVER = os.getenv("JAVA_REC_SERVER", "http://localhost:6010")
TF_SERVING_URL = os.getenv("TF_SERVING_URL", "http://localhost:8501")

# Redis 配置 (可选)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
