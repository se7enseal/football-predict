import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- 1. 数据加载与处理 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_recent_results_df(df, team):
    # 提取最近5场比赛
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5).copy()
    data_list = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        res = "胜" if (is_home and row['FTR']=='H') or (not is_home and row['FTR']=='A') else ("平" if row['FTR']=='D' else "负")
        data_list.append({
            "日期": row['Date'], 
            "对手": row['AwayTeam'] if is_home else row['HomeTeam'], 
            "比分": f"{row['FTHG']}:{row['FTAG']}", 
            "结果": res
        })
    return pd.DataFrame(data_list)

# 伤病名单库（每周赛前手动更新此处）
injury_db = {
    "Man United": "马奎尔(伤停), 卢克肖(伤停)",
    "Aston Villa": "沃特金斯(轻伤), 卡马拉(停赛)",
    "Liverpool": "无重大伤病",
    "Arsenal": "萨卡(待定)"
}

# --- 2. 页面设置 ---
st.set_page_config(page_title="足球专家分析系统", layout="wide")
st.title("⚽ 专家级全维度赛果预测系统")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    # 顶部选择区
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    # 战绩与伤病展示区
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"📊 {h_name} 近期表现")
        st.table(get_recent_results_df(data, h_name))
        st.info(f"🏥 **伤病名单:** {injury_db.get(h_name, '暂无信息')}")
    with c2:
        st.subheader(f"📊 {a_name} 近期表现")
        st.table(get_recent_results_df(data, a_name))
        st.info(f"🏥 **伤病名单:** {injury_db.get(a_name, '暂无信息')}")

    # 侧边栏修正与预测
    st.sidebar.header("📊 基本面修正")
    h_form = st.sidebar.slider(f"{h_name} 状态权重", 1, 10, 5)
    a_form = st.sidebar.slider(f"{a_name} 状态权重", 1, 10, 5)

    if st.sidebar.button("生成最终深度预测"):
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        pred_h, pred_a = int(round(h_s * (h_form/5))), int(round(a_s * (a_form/5)))
        
        st.markdown("---")
        st.subheader(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.write(f"**预计总进球:** {pred_h + pred_a} 球 | **双方是否进球:** {'是' if (pred_h > 0 and pred_a > 0) else '否'}")

        # Plotly 美观柱状图
        fig = go.Figure(data=[
            go.Bar(name='主队进攻火力', x=['对比指标'], y=[h_s], marker_color='#2E86C1'),
            go.Bar(name='客队进攻火力', x=['对比指标'], y=[a_s], marker_color='#D35400')
        ])
        fig.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("数据加载失败，请确认 'EPL_2026.csv' 文件存在于 GitHub 仓库根目录。")
