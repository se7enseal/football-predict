import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 配置 ---
TEAM_COLORS = {"Man United": "#DA291C", "Liverpool": "#C8102E", "Arsenal": "#EF0107", "Chelsea": "#034694", "Man City": "#6CABDD", "Tottenham": "#132257", "Aston Villa": "#95BFE5", "Newcastle": "#241F20", "Everton": "#003399"}

@st.cache_data(ttl=600)
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    if not os.path.exists(file_path): return None
    df = pd.read_csv(file_path)
    # 强制日期转换，确保排序准确
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df.sort_values(by='Date', ascending=False)

def get_recent_stats(df, team):
    # 强制先筛选，再按日期排序，再取前5
    team_games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].sort_values(by='Date', ascending=False).head(5)
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
    # 同样使用筛选排序后的前5场
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].sort_values(by='Date', ascending=False).head(5)
    attack = min(games.apply(lambda x: x['FTHG'] if x['HomeTeam']==team else x['FTAG'], axis=1).mean() * 3.3, 10)
    defence = max(10 - (games.apply(lambda x: x['FTAG'] if x['HomeTeam']==team else x['FTHG'], axis=1).mean() * 3.3), 0)
    points = sum([3 if (row['FTR']=='H' if row['HomeTeam']==team else row['FTR']=='A') else 1 if row['FTR']=='D' else 0 for _, row in games.iterrows()])
    state = (points / 15) * 10
    tactics = 10 - abs(attack - defence)
    # 积分离散逻辑
    team_p = df.groupby('HomeTeam')['FTHG'].count().get(team, 10)
    opp_p = df.groupby('HomeTeam')['FTHG'].count().get(opponent, 10)
    discrete_val = max(10 - abs(team_p - opp_p), 1)
    return {"进攻": round(attack,1), "防守": round(defence,1), "状态": round(state,1), "战术": round(tactics,1), "积分离散": round(discrete_val,1)}

# --- 2. 主页面 ---
st.set_page_config(layout="wide")
st.title("⚽ 专家级全维度赛果预测终端")
data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("主队", teams)
    a_name = col2.selectbox("客队", teams)

    # 近况表格
    c1, c2 = st.columns(2)
    with c1:
        h_df, h_stats = get_recent_stats(data, h_name)
        st.subheader(f"{h_name} 近况"); st.caption(f"📈 {h_stats}"); st.table(h_df)
        h_inj = st.text_input("伤病:", "无", key="h_inj")
    with c2:
        a_df, a_stats = get_recent_stats(data, a_name)
        st.subheader(f"{a_name} 近况"); st.caption(f"📈 {a_stats}"); st.table(a_df)
        a_inj = st.text_input("伤病:", "无", key="a_inj")

    # 雷达图
    h_m, a_m = calculate_radar_metrics(data, h_name, a_name), calculate_radar_metrics(data, a_name, h_name)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_m.values()), theta=list(h_m.keys()), fill='toself', name=h_name, line_color=TEAM_COLORS.get(h_name, "#2E86C1")))
    fig.add_trace(go.Scatterpolar(r=list(a_m.values()), theta=list(a_m.keys()), fill='toself', name=a_name, line_color="#FF8C00"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 【侧边栏：滑块权重】
    st.sidebar.header("🎯 预测修正权重")
    h_form = st.sidebar.slider(f"{h_name} 状态权重", 1, 10, int(np.mean(list(h_m.values()))))
    a_form = st.sidebar.slider(f"{a_name} 状态权重", 1, 10, int(np.mean(list(a_m.values()))))

    if st.button("生成最终结论"):
        pred_h = int(round(data[data['HomeTeam']==h_name]['FTHG'].mean() * (h_form/5)))
        pred_a = int(round(data[data['AwayTeam']==a_name]['FTAG'].mean() * (a_form/5)))
        st.header(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.info(f"伤病警报: {h_name}({h_inj}) vs {a_name}({a_inj})")
