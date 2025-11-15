import streamlit as st
import plotly.express as px
from analytics import movies_per_country


def render_location_analysis(filtered_df):
    """渲染地区分布页面"""
    st.header("🌍 地区分布分析")
    
    col1, col2 = st.columns([2, 1])
    
    # ==================== 各国电影数量排行 ====================
    with col1:
        st.subheader("🏢 各国家/地区电影数量")
        
        st.info("""
        **图表说明**：
        - X 轴：该国家/地区的电影数量
        - Y 轴：国家/地区名称
        - 颜色：数量越多越深
        
        **分析意义**：
        - 显示各国在全球电影中的代表作数量
        - 反映全球电影产业的格局
        """)
        
        top_n = st.slider("显示前 N 个国家/地区", min_value=5, max_value=30, value=15, step=5)
        
        country_counts = movies_per_country(filtered_df, top_n=top_n)
        
        fig = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation='h',
            labels={"x": "电影数量", "y": "国家/地区"},
            color=country_counts.values,
            color_continuous_scale="Sunset",
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            height=600,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 国家占比饼图 ====================
    with col2:
        st.subheader("🥧 国家/地区占比 (Top 10)")
        
        st.info("""
        **图表说明**：
        - 显示 Top 10 国家占总数的比例
        - 比例越大说明该国电影越多
        
        **分析意义**：
        - 如果几个国家占比很高，说明电影来源集中
        - 占比多元化说明电影选择丰富
        - 反映选片的地理多样性
        """)
        
        top_10_countries = movies_per_country(filtered_df, top_n=10)
        
        fig = px.pie(
            values=top_10_countries.values,
            names=top_10_countries.index,
            hole=0.4,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== 各国平均评分 ====================
    st.subheader("⭐ 各国家/地区平均评分 (至少5部电影)")
    
    st.info("""
    **图表说明**：
    - X 轴：各国电影的平均评分
    - Y 轴：国家/地区名称
    - 颜色：评分高低（绿=高分，红=低分）
    
    **分析意义**：
    - 显示不同国家电影的平均质量
    - 高分国家说明该国出品质量稳定
    - 可识别出"高质量出品国"
    """)
    
    country_rating = (
        filtered_df.dropna(subset=["country"])
        .groupby("country")
        .agg({"rating": ["mean", "count"]})
        .reset_index()
    )
    country_rating.columns = ["country", "avg_rating", "count"]
    country_rating = country_rating[country_rating["count"] >= 5].sort_values("avg_rating", ascending=False).head(20)
    
    fig = px.bar(
        country_rating,
        x="avg_rating",
        y="country",
        orientation='h',
        color="avg_rating",
        color_continuous_scale="RdYlGn",
        text="avg_rating",
        labels={"avg_rating": "平均评分", "country": "国家/地区"},
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # 详细数据
    st.write("**国家/地区统计数据**")
    st.dataframe(country_rating, hide_index=True, use_container_width=True)

