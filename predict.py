import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 数据加载与计算 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def calculate_metrics(df, team):
    # 获取该队最近5场
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    # 进攻：场均进球 (假设最高为 3 球，归一化到 10 分)
    attack = min(games.apply(lambda x: x['FTHG'] if x['HomeTeam']==team else x['FTAG'], axis=1).mean() * 3.3, 10)
    # 防守：场均失球 (假设场均 2 球以下为 10 分)
    defence = max(10 - (games.apply(lambda x: x['FTAG'] if x['HomeTeam']==team else x['FTHG'], axis=1).mean() * 3.3), 0)
    # 状态：积分 (最高 15 分，映射到 10 分)
    points = 0
    for _, row in games.iterrows():
        is_h = row['HomeTeam'] == team
        if (is_h and row['FTR']=='H') or (not is_h and row['FTR']=='A'): points += 3
        elif row['FTR']=='D': points += 1
    state = (points / 15) * 10
    return {"进攻": round(attack,1), "防守": round(defence,1), "状态": round(state,1)}

# --- 2. 主页面 ---
st.set_page_config(page_title="足球自动化分析", layout="wide")
st.title("⚽ 数据驱动赛果预测系统")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    h_m, a_m = calculate_metrics(data, h_name), calculate_metrics(data, a_name)
    
    # 绘制雷达图
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_m.values()), theta=list(h_m.keys()), fill='toself', name=h_name))
    fig.add_trace(go.Scatterpolar(r=list(a_m.values()), theta=list(a_m.keys()), fill='toself', name=a_name))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.plotly_chart(fig, use_container_width=True)
    

    # 预测模型
    st.sidebar.header("🎯 预测修正")
    h_form = st.sidebar.slider(f"{h_name} 最终修正分", 1, 10, int(np.mean(list(h_m.values()))))
    a_form = st.sidebar.slider(f"{a_name} 最终修正分", 1, 10, int(np.mean(list(a_m.values()))))

    if st.sidebar.button("计算预测"):
        pred_h = int(round(data[data['HomeTeam']==h_name]['FTHG'].mean() * (h_form/5)))
        pred_a = int(round(data[data['AwayTeam']==a_name]['FTAG'].mean() * (a_form/5)))
        st.subheader(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.write(f"**伤病警报:** (根据各队最新动态手动检查)")
else:
    st.error("数据加载失败。")
