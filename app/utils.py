"""工具函数和辅助模块"""

import streamlit as st
from pathlib import Path
from app.scraper import DoubanTop250Scraper
from app.analytics import load_cached_movies, movies_to_dataframe
from app.config import CACHE_PATH, SCRAPER_CONFIG


@st.cache_data
def load_data(force_refresh=False):
    """加载或爬取电影数据"""
    cache_path = Path(CACHE_PATH)
    
    if cache_path.exists() and not force_refresh:
        try:
            df = load_cached_movies(cache_path)
            return df, "从缓存加载"
        except Exception as e:
            st.warning(f"加载缓存失败: {e}，将重新爬取数据")
    
    # 爬取数据
    with st.spinner("正在爬取豆瓣电影 Top 250 数据，请稍候..."):
        scraper = DoubanTop250Scraper(**SCRAPER_CONFIG)
        movies = scraper.fetch_movies(force_refresh=force_refresh)
        df = movies_to_dataframe(movies)
        return df, "新爬取"


def init_sidebar(df):
    """初始化侧边栏"""
    st.sidebar.title("⚙️ 设置")
    st.sidebar.markdown("---")
    
    # 数据加载选项
    force_refresh = st.sidebar.button("🔄 重新爬取数据", help="重新从豆瓣网站爬取最新数据")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 数据筛选")
    
    # 确保 df 不是 None
    if df is None or len(df) == 0:
        st.sidebar.warning("⚠️ 数据加载中...")
        return force_refresh, 0, 10, []
    
    # 评分范围筛选
    try:
        min_rating = float(df["rating"].min())
        max_rating = float(df["rating"].max())
    except (KeyError, TypeError, ValueError):
        min_rating, max_rating = 0, 10
    
    rating_range = st.sidebar.slider(
        "评分范围",
        min_value=min_rating,
        max_value=max_rating,
        value=(min_rating, max_rating),
        step=0.1,
    )
    
    # 年代筛选
    try:
        decades = sorted([d for d in df["decade"].dropna().unique() if d is not None])
    except (KeyError, TypeError):
        decades = []
    
    if decades:
        selected_decades = st.sidebar.multiselect(
            "选择年代",
            options=decades,
            default=decades,
        )
    else:
        selected_decades = []
    
    return force_refresh, rating_range[0], rating_range[1], selected_decades


def apply_filters(df, min_rating, max_rating, selected_decades):
    """应用数据筛选"""
    filtered_df = df[
        (df["rating"] >= min_rating) & 
        (df["rating"] <= max_rating)
    ]
    if selected_decades:
        filtered_df = filtered_df[filtered_df["decade"].isin(selected_decades)]
    return filtered_df


def init_page_style():
    """初始化页面样式"""
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

