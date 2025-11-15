"""项目配置文件"""

# 缓存路径
CACHE_DIR = "data"
CACHE_FILE = "douban_top250.json"
CACHE_PATH = f"{CACHE_DIR}/{CACHE_FILE}"

# 爬虫配置
SCRAPER_CONFIG = {
    "cache_dir": CACHE_DIR,
    "cache_filename": CACHE_FILE,
    "use_cache": True,
    "min_delay": 1.0,
    "max_delay": 2.5,
}

# Streamlit 页面配置
STREAMLIT_CONFIG = {
    "page_title": "豆瓣电影 Top 250 数据分析",
    "page_icon": "🎬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# 数据分析配置
ANALYTICS_CONFIG = {
    "top_countries": 15,
    "top_genres": 15,
    "min_movies_for_stats": 5,
    "histogram_bins": 30,
}

# 颜色配置
COLORS = {
    "primary": "#2c3e50",
    "secondary": "#7f8c8d",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
}

