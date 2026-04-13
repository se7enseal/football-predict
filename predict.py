import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 配置项：球队经典色 ---
TEAM_COLORS = {
    "Man United": "#DA291C", "Liverpool": "#C8102E", "Arsenal": "#EF0107",
    "Chelsea": "#034694", "Man City": "#6CABDD", "Tottenham": "#132257",
    "Aston Villa": "#95BFE5", "Newcastle": "#241F20", "Everton": "#003399"
}

def get_team_color(team_name, is_second=False):
    color = TEAM_COLORS.get(team_name, "#2E86C1")
    if is_second and color == "#DA291C": return "#FF8C00"
    return color

# --- 2. 基础数据处理函数 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_recent_stats(df, team):
    """计算近5场战绩统计字符串"""
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    w, d, l = 0, 0, 0
    data_list = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        if row['FTR'] == 'D':
            res, d = "平", d + 1
        elif (is_home and row['FTR'] == 'H') or (not is_home and row['FTR'] == 'A'):
            res, w = "胜", w + 1
        else:
            res, l = "负", l + 1
        data_list.append({
            "日期": row['Date'], 
            "对手": row['AwayTeam'] if is_home else row['HomeTeam'], 
            "比分": f"{row['FTHG']}:{row['FTAG']}", 
            "结果": res
        })
    stats_str = f"近5场：{w}胜 {d}平 {l}负"
    return pd.DataFrame(data_list), stats_str

def calculate_radar_metrics(df, team):
    """自动化雷达图指标计算"""
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    # 维度计算逻辑
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
    # 球队选择
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col_sel1, col_sel2 = st.columns(2)
    h_name = col_sel1.selectbox("选择主队", teams)
    a_name = col_sel2.selectbox("选择客队", teams)

    # 1. 战绩与伤病展示区
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    # 主队部分
    with c1:
        h_df, h_stats = get_recent_stats(data, h_name)
        st.subheader(f"📊 {h_name} 近况")
        st.caption(f"📈 {h_stats}") # 使用小字标注战绩统计
        st.table(h_df)
        h_injury = st.text_input(f"{h_name} 伤病情报:", "无", key="h_inj")

    # 客队部分
    with c2:
        a_df, a_stats = get_recent_stats(data, a_name)
        st.subheader(f"📊 {a_name} 近况")
        st.caption(f"📈 {a_stats}") # 使用小字标注战绩统计
        st.table(a_df)
        a_injury = st.text_input(f"{a_name} 伤病情报:", "无", key="a_inj")

    # 2. 自动化雷达图展示
    st.markdown("---")
    h_m, a_m = calculate_radar_metrics(data, h_name), calculate_radar_metrics(data, a_name)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_m.values()), theta=list(h_m.keys()), fill='toself', name=h_name, line_color=get_team_color(h_name)))
    fig.add_trace(go.Scatterpolar(r=list(a_m.values()), theta=list(a_m.keys()), fill='toself', name=a_name, line_color=get_team_color(a_name, True)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=450)
    
    st.subheader("📊 战力多维雷达分析")
    st.plotly_chart(fig, use_container_width=True)

    # 3. 预测模型修正 (侧边栏控制)
    st.sidebar.header("🎯 模型权重微调")
    # 默认值使用雷达图所有维度的平均分
    h_init = int(np.mean(list(h_m.values())))
    a_init = int(np.mean(list(a_m.values())))
    
    h_form = st.sidebar.slider(f"{h_name} 权重", 1, 10, h_init)
    a_form = st.sidebar.slider(f"{a_name} 权重", 1, 10, a_init)

    if st.sidebar.button("开始深度预测结论"):
        # 计算场均进球作为基础
        h_avg_goal = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_avg_goal = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        # 应用手动权重修正
        pred_h = int(round(h_avg_goal * (h_form/5)))
        pred_a = int(round(a_avg_goal * (a_form/5)))
        
        st.markdown("---")
        st.header(f"🎯 最终比分预测：{pred_h} : {pred_a}")
        st.write(f"**总进球预期：** {pred_h + pred_a} | **双方进球：** {'是' if (pred_h > 0 and pred_a > 0) else '否'}")
        st.warning(f"💡 专家建议关注：{h_name} 伤病({h_injury})，{a_name} 伤病({a_injury})。")

else:
    st.error("数据加载失败，请检查根目录下是否存在 EPL_2026.csv。")
