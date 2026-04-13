import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 颜色配置系统 ---
TEAM_COLORS = {
    "Man United": "#DA291C", "Liverpool": "#C8102E", "Arsenal": "#EF0107",
    "Chelsea": "#034694", "Man City": "#6CABDD", "Tottenham": "#132257",
    "Aston Villa": "#95BFE5", "Newcastle": "#241F20", "Everton": "#003399"
}

def get_team_color(team_name, is_second=False, other_color=None):
    """获取球队色，若冲突则强制使用对比色"""
    color = TEAM_COLORS.get(team_name, "#2E86C1")
    # 如果是第二支球队且颜色与第一支重复，强制切换为对比色
    if is_second and color == other_color:
        return "#FF8C00" # 橙色，与红色/蓝色有极高对比度
    return color

# --- 2. 基础数据处理与统计 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_recent_stats(df, team):
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    w, d, l = 0, 0, 0
    data_list = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        if row['FTR'] == 'D': res, d = "平", d + 1
        elif (is_home and row['FTR'] == 'H') or (not is_home and row['FTR'] == 'A'): res, w = "胜", w + 1
        else: res, l = "负", l + 1
        data_list.append({"日期": row['Date'], "对手": row['AwayTeam'] if is_home else row['HomeTeam'], "比分": f"{row['FTHG']}:{row['FTAG']}", "结果": res})
    return pd.DataFrame(data_list), f"{w}胜 {d}平 {l}负"

def calculate_radar_metrics(df, team):
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    attack = min(games.apply(lambda x: x['FTHG'] if x['HomeTeam']==team else x['FTAG'], axis=1).mean() * 3.3, 10)
    defence = max(10 - (games.apply(lambda x: x['FTAG'] if x['HomeTeam']==team else x['FTHG'], axis=1).mean() * 3.3), 0)
    points = sum([3 if (row['FTR']=='H' if row['HomeTeam']==team else row['FTR']=='A') else 1 if row['FTR']=='D' else 0 for _, row in games.iterrows()])
    state = (points / 15) * 10
    tactics = 10 - abs(attack - defence)
    return {"进攻": round(attack,1), "防守": round(defence,1), "近期状态": round(state,1), "战术能力": round(tactics,1), "积分排名": 7.0}

# --- 3. 页面主程序 ---
st.set_page_config(page_title="足球大师分析终端", layout="wide")
st.title("⚽ 专家级全维度赛果预测终端")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col_sel1, col_sel2 = st.columns(2)
    h_name = col_sel1.selectbox("选择主队", teams)
    a_name = col_sel2.selectbox("选择客队", teams)

    # 战绩展示
    c1, c2 = st.columns(2)
    with c1:
        h_df, h_stats = get_recent_stats(data, h_name)
        st.subheader(f"📊 {h_name} 近况")
        st.caption(f"📈 近5场：{h_stats}")
        st.table(h_df)
        h_injury = st.text_input("伤病情报:", "无", key="h_inj")
    with c2:
        a_df, a_stats = get_recent_stats(data, a_name)
        st.subheader(f"📊 {a_name} 近况")
        st.caption(f"📈 近5场：{a_stats}")
        st.table(a_df)
        a_injury = st.text_input("伤病情报:", "无", key="a_inj")

    # 雷达图逻辑 (集成颜色检测)
    h_m, a_m = calculate_radar_metrics(data, h_name), calculate_radar_metrics(data, a_name)
    h_col = get_team_color(h_name)
    a_col = get_team_color(a_name, is_second=True, other_color=h_col)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_m.values()), theta=list(h_m.keys()), fill='toself', name=h_name, line_color=h_col))
    fig.add_trace(go.Scatterpolar(r=list(a_m.values()), theta=list(a_m.keys()), fill='toself', name=a_name, line_color=a_col))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.subheader("📊 战力多维雷达分析")
    st.plotly_chart(fig, use_container_width=True)

    # 预测模型
    st.sidebar.header("🎯 模型权重微调")
    h_form = st.sidebar.slider(f"{h_name} 状态权重", 1, 10, int(np.mean(list(h_m.values()))))
    a_form = st.sidebar.slider(f"{a_name} 状态权重", 1, 10, int(np.mean(list(a_m.values()))))

    if st.button("生成最终结论"):
        pred_h = int(round(data[data['HomeTeam']==h_name]['FTHG'].mean() * (h_form/5)))
        pred_a = int(round(data[data['AwayTeam']==a_name]['FTAG'].mean() * (a_form/5)))
        st.header(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.info(f"伤病警报: {h_name}({h_injury}) | {a_name}({a_injury})")

else:
    st.error("数据加载失败。")
