import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 数据加载 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_recent_results_df(df, team):
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5).copy()
    data_list = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        res = "胜" if (is_home and row['FTR']=='H') or (not is_home and row['FTR']=='A') else ("平" if row['FTR']=='D' else "负")
        data_list.append({"日期": row['Date'], "对手": row['AwayTeam'] if is_home else row['HomeTeam'], "比分": f"{row['FTHG']}:{row['FTAG']}", "结果": res})
    return pd.DataFrame(data_list)

# --- 2. 页面布局 ---
st.set_page_config(page_title="足球预测系统", layout="wide")
st.title("⚽ 专家级多维度赛果预测终端")

data = load_data()

if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)
    
    # 战绩与伤病展示区
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"📊 {h_name} 近况")
        st.table(get_recent_results_df(data, h_name))
        h_injury = st.text_input(f"手动输入 {h_name} 伤病名单:", "无")
    with c2:
        st.subheader(f"📊 {a_name} 近况")
        st.table(get_recent_results_df(data, a_name))
        a_injury = st.text_input(f"手动输入 {a_name} 伤病名单:", "无")

    # 雷达图数据维度 (手动输入，方便你调整)
    st.sidebar.header("📊 雷达图维度调整")
    h_radar = [st.sidebar.slider(f"主队-{d}", 1, 10, 5) for d in ["进攻", "防守", "战术", "排名", "状态"]]
    a_radar = [st.sidebar.slider(f"客队-{d}", 1, 10, 5) for d in ["进攻", "防守", "战术", "排名", "状态"]]
    
    # 滑块评分 (最终决策权重)
    st.sidebar.header("🎯 最终权重修正")
    h_form = st.sidebar.slider(f"{h_name} 状态权重", 1, 10, 5)
    a_form = st.sidebar.slider(f"{a_name} 状态权重", 1, 10, 5)

    if st.sidebar.button("生成最终结论"):
        # 绘制雷达图
        categories = ["进攻", "防守", "战术", "排名", "状态"]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=h_radar, theta=categories, fill='toself', name=h_name))
        fig.add_trace(go.Scatterpolar(r=a_radar, theta=categories, fill='toself', name=a_name))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 预测模型
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        pred_h, pred_a = int(round(h_s * (h_form/5))), int(round(a_s * (a_form/5)))
        
        st.subheader(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.write(f"**伤病警报:** {h_name}: {h_injury} | {a_name}: {a_injury}")
else:
    st.error("找不到数据文件，请确认 'EPL_2026.csv' 路径。")
