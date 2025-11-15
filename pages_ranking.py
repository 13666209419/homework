import streamlit as st
import plotly.express as px


def render_ranking(filtered_df):
    """渲染排行榜页面"""
    st.header("🏆 电影排行榜")
    
    col1, col2 = st.columns(2)
    
    # ==================== 评分最高的电影 ====================
    with col1:
        st.subheader("🏅 评分最高的电影 (Top 15)")
        
        st.info("""
        **图表说明**：
        - X 轴：电影评分（1-10分）
        - Y 轴：电影名称
        - 颜色：评分高低（深红色=高分）
        
        **分析意义**：
        - 反映豆瓣用户认可度最高的电影
        - 通常是经典佳作
        - 可作为高质量观影参考
        """)
        
        top_rated = filtered_df.nlargest(15, "rating")[["rank", "title", "year", "rating", "votes"]]
        
        fig = px.bar(
            top_rated,
            x="rating",
            y="title",
            orientation="h",
            color="rating",
            color_continuous_scale="YlOrRd",
            text="rating",
            labels={"rating": "评分", "title": "电影名称"},
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            height=500,
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示详细数据
        st.write("**详细数据**")
        st.dataframe(top_rated, hide_index=True, use_container_width=True)
    
    # ==================== 评价人数最多的电影 ====================
    with col2:
        st.subheader("👥 评价人数最多的电影 (Top 15)")
        
        st.info("""
        **图表说明**：
        - X 轴：评价人数（参与评分的用户数）
        - Y 轴：电影名称
        - 颜色：热度（深蓝色=最热门）
        
        **分析意义**：
        - 反映电影的热度和讨论度
        - 评价人数多说明电影知名度高
        - 可能包括热点电影、大制作等
        - 不一定评分最高，但最受关注
        """)
        
        most_voted = filtered_df.nlargest(15, "votes")[["rank", "title", "year", "rating", "votes"]]
        
        fig = px.bar(
            most_voted,
            x="votes",
            y="title",
            orientation="h",
            color="votes",
            color_continuous_scale="Blues",
            text="votes",
            labels={"votes": "评价人数", "title": "电影名称"},
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            height=500,
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示详细数据
        st.write("**详细数据**")
        st.dataframe(most_voted, hide_index=True, use_container_width=True)

