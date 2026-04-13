import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 配置项 ---
TEAM_COLORS = {
    "Man United": "#DA291C", "Liverpool": "#C8102E", "Arsenal": "#EF0107",
    "Chelsea": "#034694", "Man City": "#6CABDD", "Tottenham": "#132257",
    "Aston Villa": "#95BFE5", "Newcastle": "#241F20", "Everton": "#003399"
}

def get_team_color(team_name, is_second=False):
    color = TEAM_COLORS.get(team_name, "#2E86C1")
    if is_second and color == "#DA291C": return "#FF8C00"
    return color

# --- 2. 核心功能函数 ---
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

def calculate_radar_metrics(df, team):
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    # 逻辑计算维度
    attack = min(games.apply(lambda x: x['FTHG'] if x['HomeTeam']==team else x['FTAG'], axis=1).mean() * 3.3, 10)
    defence = max(10 - (games.apply(lambda x: x['FTAG'] if x['HomeTeam']==team else x['FTHG'], axis=1).mean() * 3.3), 0)
    points = sum([3 if (row['FTR']=='H' if row['HomeTeam']==team else row['FTR']=='A') else 1 if row['FTR']=='D' else 0 for _, row in games.iterrows()])
    state = (points / 15) * 10
    tactics = 10 - abs(attack - defence)
    return {"进攻": round(attack,1), "防守": round(defence,1), "近期状态": round(state,1), "战术能力": round(tactics,1), "积分排名": 7.0}

# --- 3. 页面主程序 (集成所有功能) ---
st.set_page_config(page_title="足球分析终端", layout="wide")
st.title("⚽ 专家级全维度赛果预测终端")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    # 1. 战绩与伤病展示
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"📊 {h_name} 近况")
        st.table(get_recent_results_df(data, h_name))
        h_injury = st.text_input(f"{h_name} 伤病:", "无", key="h_inj")
    with c2:
        st.subheader(f"📊 {a_name} 近况")
        st.table(get_recent_results_df(data, a_name))
        a_injury = st.text_input(f"{a_name} 伤病:", "无", key="a_inj")

    # 2. 自动生成雷达图
    h_m, a_m = calculate_radar_metrics(data, h_name), calculate_radar_metrics(data, a_name)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_m.values()), theta=list(h_m.keys()), fill='toself', name=h_name, line_color=get_team_color(h_name)))
    fig.add_trace(go.Scatterpolar(r=list(a_m.values()), theta=list(a_m.keys()), fill='toself', name=a_name, line_color=get_team_color(a_name, True)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.subheader("📊 战力多维雷达分析")
    st.plotly_chart(fig, use_container_width=True)

    # 3. 预测模块
    st.sidebar.header("🎯 预测修正")
    h_form = st.sidebar.slider(f"{h_name} 权重", 1, 10, int(np.mean(list(h_m.values()))))
    a_form = st.sidebar.slider(f"{a_name} 权重", 1, 10, int(np.mean(list(a_m.values()))))

    if st.sidebar.button("生成最终结论"):
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        pred_h, pred_a = int(round(h_s * (h_form/5))), int(round(a_s * (a_form/5)))
        
        st.markdown("---")
        st.header(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.write(f"**预计总进球:** {pred_h + pred_a} | **双方是否进球:** {'是' if (pred_h > 0 and pred_a > 0) else '否'}")
        st.info(f"伤病警报: {h_name}({h_injury}) | {a_name}({a_injury})")
else:
    st.error("数据加载失败。")
