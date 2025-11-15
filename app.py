"""
豆瓣电影 Top 250 数据分析 Streamlit 应用

这是主入口文件，协调所有页面和模块。
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 确保可以导入本地模块
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from config import STREAMLIT_CONFIG
from utils import load_data, init_sidebar, apply_filters, init_page_style
from pages_overview import render_overview
from pages_ranking import render_ranking
from pages_rating import render_rating_analysis
from pages_location import render_location_analysis
from pages_genre import render_genre_analysis


def main():
    """主应用入口"""
    # 页面配置
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # 初始化样式
    init_page_style()
    
    # 标题
    st.markdown('<div class="main-header">🎬 豆瓣电影 Top 250 数据分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">探索全球最受欢迎的 250 部电影</div>', unsafe_allow_html=True)
    
    # 加载数据
    try:
        # 先加载数据
        df, source = load_data(False)
        
        # 初始化侧边栏获取筛选参数
        force_refresh, min_rating, max_rating, selected_decades = init_sidebar(df)
        
        # 如果点击刷新按钮，重新加载
        if force_refresh:
            df, source = load_data(True)
            st.sidebar.success(f"✅ 数据{source}成功")
            st.rerun()
        else:
            st.sidebar.success(f"✅ 数据{source}成功")
        
        st.sidebar.info(f"📊 共 {len(df)} 部电影")
        
    except Exception as e:
        st.error(f"❌ 加载数据失败: {e}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
        st.stop()
    
    # 应用筛选
    filtered_df = apply_filters(df, min_rating, max_rating, selected_decades)
    
    # 创建页面标签
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 数据总览",
        "🏆 排行榜",
        "📈 评分分析",
        "🌍 地区分布",
        "🎭 类型分析"
    ])
    
    # 各页面内容
    with tab1:
        render_overview(filtered_df, df)
    
    with tab2:
        render_ranking(filtered_df)
    
    with tab3:
        render_rating_analysis(filtered_df)
    
    with tab4:
        render_location_analysis(filtered_df)
    
    with tab5:
        render_genre_analysis(filtered_df)
    
    # 页脚
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #7f8c8d;">
            <p>数据来源: <a href="https://movie.douban.com/top250" target="_blank">豆瓣电影 Top 250</a></p>
            <p>仅供学习和研究使用</p>
            <p style="font-size: 0.9em; margin-top: 1rem;">项目架构: 数据爬虫 → Pandas 分析 → Streamlit 可视化</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
