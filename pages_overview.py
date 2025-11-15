import streamlit as st
from analytics import rating_summary, votes_summary


def render_overview(filtered_df, df):
    """渲染数据总览页面"""
    st.header("📊 数据总览")
    
    # ==================== 关键指标卡片 ====================
    st.subheader("关键指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="电影总数",
            value=f"{len(filtered_df)}",
            delta=f"{len(filtered_df) - len(df)}" if len(filtered_df) != len(df) else None,
        )
    
    with col2:
        avg_rating = filtered_df["rating"].mean()
        st.metric(
            label="平均评分",
            value=f"{avg_rating:.2f}",
        )
    
    with col3:
        total_votes = filtered_df["votes"].sum()
        st.metric(
            label="总评价人数",
            value=f"{total_votes:,}",
        )
    
    with col4:
        countries_count = filtered_df["country"].nunique()
        st.metric(
            label="涉及国家/地区",
            value=f"{countries_count}",
        )
    
    st.markdown("---")
    
    # ==================== 统计表格 ====================
    st.subheader("📈 统计数据")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**评分统计**")
        st.info("""
        - Count: 数据量
        - Mean: 平均值
        - Std: 标准差（数据波动程度）
        - Min/Max: 最小/最大值
        - 25%/50%/75%: 四分位数
        """)
        rating_stats = rating_summary(filtered_df)
        st.dataframe(rating_stats.to_frame("评分"), use_container_width=True)
    
    with col2:
        st.write("**评价人数统计**")
        st.info("""
        表明评价人数的分布情况。
        数值越高说明越多人评价，
        电影越热门/经典。
        """)
        votes_stats = votes_summary(filtered_df)
        st.dataframe(votes_stats.to_frame("评价人数"), use_container_width=True)
    
    st.markdown("---")
    
    # ==================== 数据预览表 ====================
    st.subheader("📋 数据预览（前20部电影）")
    
    display_columns = ["rank", "title", "original_title", "year", "country", "rating", "votes", "all_genres"]
    column_config = {
        "rank": "排名",
        "title": "电影名称",
        "original_title": "原始片名",
        "year": "年份",
        "country": "国家/地区",
        "rating": "评分",
        "votes": "评价人数",
        "all_genres": "类型",
    }
    
    st.dataframe(
        filtered_df[display_columns].head(20),
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
    )
    
    # 数据说明
    st.info("""
    💡 **数据说明**
    - **排名**: 豆瓣 Top 250 排名
    - **评分**: 1-10 分制，越高越好
    - **评价人数**: 参与评分的用户数，反映电影热度
    - **国家/地区**: 电影制作国家/地区
    - **类型**: 电影分类（可能有多个）
    """)

