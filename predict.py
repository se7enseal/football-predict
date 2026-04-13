import streamlit as st
import pandas as pd
import os

# --- 1. 数据处理区 ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_stats(df, team):
    # 过滤主客场比赛
    home_games = df[df['HomeTeam'] == team]
    away_games = df[df['AwayTeam'] == team]
    
    # 平均进球与失球
    h_scored = home_games['FTHG'].mean()
    h_conceded = home_games['FTAG'].mean()
    a_scored = away_games['FTG'].mean() # 假设CSV包含客场进球列
    a_conceded = away_games['FTHG'].mean()
    
    return h_scored, h_conceded, a_scored, a_conceded

# --- 2. 网页 UI ---
st.title("⚽ 足球专家级深度分析系统")
data = load_data()

if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    if st.button("开始深度预测"):
        h_s, h_c, _, _ = get_stats(data, h_name)
        _, _, a_s, a_c = get_stats(data, a_name)
        
        # 简单比分模型 (预测进球 = 主攻能力 * 客防能力)
        pred_h = round((h_s + a_c) / 2)
        pred_a = round((a_s + h_c) / 2)
        
        st.subheader(f"📊 预测比分: {pred_h} : {pred_a}")
        
        # 进球数与 BTTS
        total_goals = pred_h + pred_a
        btts = "是" if (pred_h > 0 and pred_a > 0) else "否"
        
        st.write(f"**预计总进球数:** {total_goals} 球")
        st.write(f"**双方是否进球 (BTTS):** {btts}")
        
        # 爆冷提示
        if abs(pred_h - pred_a) <= 1:
            st.warning("⚠️ 提示：比分差距小，模型预测为焦灼对局，谨防平局。")
else:
    st.error("数据文件加载失败，请检查路径。")
