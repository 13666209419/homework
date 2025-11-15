import streamlit as st
import pandas as pd
import plotly.express as px
import itertools
from collections import Counter
from src.analytics import genre_popularity


def render_genre_analysis(filtered_df):
    """类型分析主函数"""
    st.header("🎭 电影类型分析")
    
    col1, col2 = st.columns(2)
    
    # ==================== 各类型电影数量 ====================
    with col1:
        st.subheader("📊 各类型电影数量 (Top 15)")
        
        st.info("""
        **图表说明**：
        - X 轴：该类型的电影数量
        - Y 轴：电影类型（独立的单个类型）
        - 颜色：数量越多越深（紫色最深）
    
        
        **分析意义**：
        - 显示 Top 250 中各类型的代表作数量
        - 剧情类通常最多（最基础的分类）
        - 数量多说明该类型更受欢迎
        - 可用于了解选片的类型构成
        """)
        
        # 分离空格分隔的多个类型
        all_genres = []
        for genres_list in filtered_df["genres"]:
            if genres_list:
                for genre_str in genres_list:
                    # 按空格分割每个类型字符串，得到独立的类型
                    individual_genres = genre_str.split()
                    all_genres.extend(individual_genres)
        
        # 统计每个类型出现的次数
        genre_counts_dict = Counter(all_genres)
        genre_counts = pd.Series(dict(sorted(genre_counts_dict.items(), key=lambda x: x[1], reverse=True)[:15]))
        
        fig = px.bar(
            x=genre_counts.values,
            y=genre_counts.index,
            orientation='h',
            labels={"x": "电影数量", "y": "类型"},
            color=genre_counts.values,
            color_continuous_scale="Plasma",
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 各类型平均评分 ====================
    with col2:
        st.subheader("⭐ 各类型平均评分 (Top 15)")
        
        st.info("""
        **图表说明**：
        - X 轴：该类型电影的平均评分
        - Y 轴：电影类型（独立的单个类型）
        - 颜色：评分高低（绿=高分，红=低分）

        **分析意义**：
        - 显示不同类型的平均质量水平
        - 高分类型说明该类型的作品质量稳定
        - 可识别"品质保证"的类型
        - 如：某些历史类型平均分常较高
        """)
        
        # 分离空格分隔的多个类型，并计算每个独立类型的平均评分
        genre_data = []
        for _, row in filtered_df.iterrows():
            rating = row["rating"]
            genres_list = row["genres"]
            if genres_list:
                for genre_str in genres_list:
                    # 按空格分割每个类型字符串，得到独立的类型
                    individual_genres = genre_str.split()
                    for genre in individual_genres:
                        genre_data.append({"genre": genre, "rating": rating})
        
        genre_df = pd.DataFrame(genre_data)
        genre_rating = (
            genre_df.groupby("genre", as_index=False)
            .agg(avg_rating=("rating", "mean"), count=("rating", "count"))
        )
        # 只展示电影数量不少于5的类型，并取前15个平均分最高的类型
        genre_rating = genre_rating[genre_rating["count"] >= 5].sort_values("avg_rating", ascending=False).head(15)
        
        fig = px.bar(
            genre_rating,
            x="avg_rating",
            y="genre",
            orientation='h',
            color="avg_rating",
            color_continuous_scale="RdYlGn",
            text="avg_rating",
            labels={"avg_rating": "平均评分", "genre": "类型"},
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            height=500,
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== 类型共现热力图 ====================
    st.subheader("🔥 类型共现热力图 (Top 10 类型)")
    
    st.info("""
    **图表说明**：
    - 行和列：电影类型（独立的单个类型）
    - 颜色强度和数字：两种类型同时出现的次数
    - 颜色越深=共现越频繁
    - 对角线=每种类型出现的总次数

  
    **分析意义**：
    - 显示哪些类型经常组合出现
    - 反映电影的跨类型特征
    - 对制片方了解市场需求有帮助
    """)
    
    # 先获取排名前10的独立类型
    all_genres_list = []
    for genres_list in filtered_df["genres"]:
        if genres_list:
            for genre_str in genres_list:
                individual_genres = genre_str.split()
                all_genres_list.extend(individual_genres)
    
    genre_counts_dict = Counter(all_genres_list)
    top_genres = [g for g, _ in genre_counts_dict.most_common(10)]
    
    # 创建类型共现矩阵，任意类型对出现计算一次
    cooccurrence = pd.DataFrame(0, index=top_genres, columns=top_genres)
    
    for _, row in filtered_df.iterrows():
        genres_list = row["genres"]
        if genres_list:
            # 从每个genre_str中分离独立的类型
            individual_genres = []
            for genre_str in genres_list:
                individual_genres.extend(genre_str.split())
            
            # 获取属于top10的类型
            relevant_genres = [g for g in individual_genres if g in top_genres]
            
            if len(relevant_genres) > 0:
                # 计算所有类型对的共现
                for g1, g2 in itertools.combinations_with_replacement(relevant_genres, 2):
                    cooccurrence.loc[g1, g2] += 1
                    if g1 != g2:
                        cooccurrence.loc[g2, g1] += 1  # 保证对称

    fig = px.imshow(
        cooccurrence,
        labels=dict(x="类型", y="类型", color="共现次数"),
        color_continuous_scale="YlOrRd",
        text_auto=True,
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # 详细数据
    st.write("**类型统计数据**")
    st.dataframe(genre_rating, hide_index=True, use_container_width=True)

