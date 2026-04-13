import streamlit as st
import pandas as pd
import os

# --- 1. 数据加载 ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

# --- 2. 核心统计逻辑 ---
def get_stats(df, team):
    # 过滤比赛
    home_games = df[df['HomeTeam'] == team]
    away_games = df[df['AwayTeam'] == team]
    
    # 计算平均进球 (FTHG 为主进球, FTAG 为客进球)
    h_scored_avg = home_games['FTHG'].mean()
    h_conceded_avg = home_games['FTAG'].mean()
    a_scored_avg = away_games['FTAG'].mean()
    a_conceded_avg = away_games['FTHG'].mean()
    
    return h_scored_avg, h_conceded_avg, a_scored_avg, a_conceded_avg

# --- 3. 网页交互区 ---
st.title("⚽ 足球深度分析系统")
data = load_data()

if data is not None:
    # 获取所有球队名
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    h_name = st.sidebar.selectbox("选择主队", teams)
    a_name = st.sidebar.selectbox("选择客队", teams)

    if st.sidebar.button("开始深度预测"):
        # 获取两队数据
        h_s, h_c, _, _ = get_stats(data, h_name)
        _, _, a_s, a_c = get_stats(data, a_name)
        
        # 简单比分模型: (主队进球期望 + 客队失球期望) / 2
        pred_h = round((h_s + a_c) / 2)
        pred_a = round((a_s + h_c) / 2)
        
        st.subheader(f"📊 预测比分: {pred_h} : {pred_a}")
        
        # 进球数与 BTTS (Both Teams To Score)
        total_goals = pred_h + pred_a
        btts = "是" if (pred_h > 0 and pred_a > 0) else "否"
        
        st.write(f"**预计总进球数:** {total_goals} 球")
        st.write(f"**双方是否进球 (BTTS):** {btts}")
else:
    st.error("找不到文件，请确认 GitHub 仓库中文件名是否为 EPL_2026.csv")
