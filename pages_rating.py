import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render_rating_analysis(filtered_df):
    """渲染评分分析页面"""
    st.header("📈 评分分析")
    
    col1, col2 = st.columns(2)
    
    # ==================== 评分分布直方图 ====================
    with col1:
        st.subheader("📊 评分分布直方图")
        
        st.info("""
        **图表说明**：
        - X 轴：电影评分段（0.1 分为一个间隔）
        - Y 轴：电影数量
        
        **分析意义**：
        - 显示哪个评分区间的电影最多
        - 如果呈正态分布，说明评分相对均衡
        - 如果偏向高分，说明 Top 250 大多是佳作
        - 用于理解整体评分水平
        """)
        
        fig = px.histogram(
            filtered_df,
            x="rating",
            nbins=30,
            labels={"rating": "评分", "count": "电影数量"},
            color_discrete_sequence=["#3498db"],
        )
        fig.update_layout(
            showlegend=False,
            bargap=0.1,
            xaxis_title="评分",
            yaxis_title="电影数量",
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 评分 vs 评价人数散点图 ====================
    with col2:
        st.subheader("📍 评分 vs 评价人数")
        
        st.info("""
        **图表说明**：
        - X 轴：评价人数（对数坐标）
        - Y 轴：电影评分
        - 点的大小：评价人数（越大越热门）
        - 颜色：评分高低
        
        **分析意义**：
        - 寻找"高分冷门"：右上角评分高但评价少
        - 寻找"低分热门"：左下角评分低但评价多（通常没有）
        - 一般来说，热门电影评分不会太低
        - 用于发现被低估或高估的电影
        """)
        
        fig = px.scatter(
            filtered_df,
            x="votes",
            y="rating",
            hover_data=["title", "year"],
            color="rating",
            size="votes",
            color_continuous_scale="Viridis",
            labels={"votes": "评价人数", "rating": "评分"},
        )
        fig.update_layout(
            showlegend=False,
            xaxis_type="log",  # 对数坐标便于展示跨度大的数据
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== 年代评分趋势双轴图 ====================
    st.subheader("📅 年代评分趋势分析")
    
    st.info("""
    **图表说明**：
    - 红色折线：各年代的平均评分（左轴）
    - 蓝色柱子：各年代的电影数量（右轴）
    
    **分析意义**：
    - 显示不同年代电影的质量走势
    - 电影数量多说明该年代的热门/经典电影更多
    - 平均评分高说明该年代的电影质量好
    - 可以发现"黄金年代"和"衰落期"
    """)
    
    decade_rating = (
        filtered_df.dropna(subset=["decade"])
        .groupby("decade")
        .agg({"rating": ["mean", "count"]})
        .reset_index()
    )
    decade_rating.columns = ["decade", "avg_rating", "count"]
    decade_rating = decade_rating.sort_values("decade")
    
    fig = go.Figure()
    
    # 折线图：平均评分
    fig.add_trace(go.Scatter(
        x=decade_rating["decade"],
        y=decade_rating["avg_rating"],
        mode='lines+markers',
        name='平均评分',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10),
        yaxis='y',
    ))
    
    # 柱状图：电影数量
    fig.add_trace(go.Bar(
        x=decade_rating["decade"],
        y=decade_rating["count"],
        name='电影数量',
        yaxis='y2',
        opacity=0.3,
        marker=dict(color='#3498db'),
    ))
    
    fig.update_layout(
        yaxis=dict(
            title=dict(text="平均评分", font=dict(color='#e74c3c')),
            tickfont=dict(color='#e74c3c'),
        ),
        yaxis2=dict(
            title=dict(text="电影数量", font=dict(color='#3498db')),
            overlaying='y',
            side='right',
            tickfont=dict(color='#3498db'),
        ),
        xaxis=dict(title="年代"),
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99),
        height=500,
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 详细数据
    st.write("**年代统计数据**")
    st.dataframe(decade_rating, hide_index=True, use_container_width=True)

