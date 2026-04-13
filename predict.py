import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 配置系统 ---
TEAM_COLORS = {
    "Man United": "#DA291C", "Liverpool": "#C8102E", "Arsenal": "#EF0107",
    "Chelsea": "#034694", "Man City": "#6CABDD", "Tottenham": "#132257",
    "Aston Villa": "#95BFE5", "Newcastle": "#241F20", "Everton": "#003399"
}

def get_team_color(team_name, is_second=False, other_color=None):
    color = TEAM_COLORS.get(team_name, "#2E86C1")
    if is_second and color == other_color: return "#FF8C00"
    return color

# --- 2. 核心分析逻辑 ---
@st.cache_data(ttl=600)
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    if not os.path.exists(file_path): return None
    df = pd.read_csv(file_path)
    # 【核心修复】统一将日期转换为 datetime 对象，并确保全局倒序
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df.sort_values(by='Date', ascending=False)

def get_recent_stats(df, team):
    # 动态切片：找到该队在整个CSV中出现过的所有比赛，并取时间上最新的5场
    team_games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].head(5)
    w, d, l = 0, 0, 0
    data_list = []
    for _, row in team_games.iterrows():
        is_home = row['HomeTeam'] == team
        if row['FTR'] == 'D': res, d = "平", d + 1
        elif (is_home and row['FTR'] == 'H') or (not is_home and row['FTR'] == 'A'): res, w = "胜", w + 1
        else: res, l = "负", l + 1
        data_list.append({"日期": row['Date'].strftime('%m-%d'), "对手": row['AwayTeam'] if is_home else row['HomeTeam'], "比分": f"{row['FTHG']}:{row['FTAG']}", "结果": res})
    return pd.DataFrame(data_list), f"{w}胜 {d}平 {l}负"

def calculate_radar_metrics(df, team, opponent):
    # 同样使用动态切片
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].head(5)
    attack = min(games.apply(lambda x: x['FTHG'] if x['HomeTeam']==team else x['FTAG'], axis=1).mean() * 3.3, 10)
    defence = max(10 - (games.apply(lambda x: x['FTAG'] if x['HomeTeam']==team else x['FTHG'], axis=1).mean() * 3.3), 0)
    points_earned = sum([3 if (row['FTR']=='H' if row['HomeTeam']==team else row['FTR']=='A') else 1 if row['FTR']=='D' else 0 for _, row in games.iterrows()])
    state = (points_earned / 15) * 10
    tactics = 10 - abs(attack - defence)
    
    # 离散值：动态计算当前数据集中的总场次作为排名参考
    team_p = df.groupby('HomeTeam')['FTHG'].count().get(team, 10)
    opp_p = df.groupby('HomeTeam')['FTHG'].count().get(opponent, 10)
    discrete_val = max(10 - abs(team_p - opp_p), 1)
    
    return {"进攻": round(attack,1), "防守": round(defence,1), "状态": round(state,1), "战术": round(tactics,1), "积分离散": round(discrete_val,1)}

# --- 3. 页面主程序 ---
st.set_page_config(page_title="足球预测系统", layout="wide")
st.title("⚽ 智能回溯赛果预测终端")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    c1, c2 = st.columns(2)
    with c1:
        h_df, h_stats = get_recent_stats(data, h_name)
        st.subheader(f"📊 {h_name} 近况")
        st.caption(f"📈 {h_stats}")
        st.table(h_df)
        h_injury = st.text_input("伤病情报:", "无", key="h_inj")
    with c2:
        a_df, a_stats = get_recent_stats(data, a_name)
        st.subheader(f"📊 {a_name} 近况")
        st.caption(f"📈 {a_stats}")
        st.table(a_df)
        a_injury = st.text_input("伤病情报:", "无", key="a_inj")

    h_m, a_m = calculate_radar_metrics(data, h_name, a_name), calculate_radar_metrics(data, a_name, h_name)
    h_col = get_team_color(h_name)
    a_col = get_team_color(a_name, True, h_col)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_m.values()), theta=list(h_m.keys()), fill='toself', name=h_name, line_color=h_col))
    fig.add_trace(go.Scatterpolar(r=list(a_m.values()), theta=list(a_m.keys()), fill='toself', name=a_name, line_color=a_col))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.subheader("📊 战力多维雷达分析")
    st.plotly_chart(fig, use_container_width=True)

    st.sidebar.header("🎯 模型权重微调")
    h_form = st.sidebar.slider(f"{h_name} 权重", 1, 10, int(np.mean(list(h_m.values()))))
    a_form = st.sidebar.slider(f"{a_name} 权重", 1, 10, int(np.mean(list(a_m.values()))))

    if st.button("生成深度结论"):
        pred_h = int(round(data[data['HomeTeam']==h_name]['FTHG'].mean() * (h_form/5)))
        pred_a = int(round(data[data['AwayTeam']==a_name]['FTAG'].mean() * (a_form/5)))
        st.header(f"🎯 最终预测比分: {pred_h} : {pred_a}")
        st.info(f"伤病警报: {h_name}({h_injury}) | {a_name}({a_injury})")
else:
    st.error("数据加载失败。")
