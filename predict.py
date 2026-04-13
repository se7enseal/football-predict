import streamlit as st
import pandas as pd
import os

# --- 1. 数据加载 ---
@st.cache_data
def load_data():
    # 自动获取当前代码所在路径，确保即使在云端也能找到同目录下的文件
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'EPL_2026.csv')
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

# --- 2. 积分计算逻辑 ---
def get_team_points(df):
    if df is None: return {}
    # 提取所有出现的球队名称
    teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    points = {team: 0 for team in teams}
    
    for _, row in df.iterrows():
        # 这里对应 Football-Data 格式：FTR 为 'H'主胜, 'A'客胜, 'D'平局
        if row['FTR'] == 'H':
            points[row['HomeTeam']] += 3
        elif row['FTR'] == 'A':
            points[row['AwayTeam']] += 3
        else:
            points[row['HomeTeam']] += 1
            points[row['AwayTeam']] += 1
    return points

# --- 3. 页面核心 ---
st.title("⚽ 足球赛果智能预测系统")

# 加载数据并检测错误
data = load_data()

if data is not None:
    team_scores = get_team_points(data)
    
    # 用户输入交互
    st.sidebar.header("输入预测对阵")
    home_team = st.sidebar.text_input("主队名称 (如: Arsenal)")
    away_team = st.sidebar.text_input("客队名称 (如: Everton)")

    if st.sidebar.button("开始预测"):
        if home_team in team_scores and away_team in team_scores:
            diff = team_scores[home_team] - team_scores[away_team]
            
            # 显示离散结果
            if diff > 10: res = "主队实力碾压 - 预测主胜"
            elif diff < -10: res = "客队实力强劲 - 预测客胜"
            else: res = "双方势均力敌 - 预测平局或小比分"
            
            st.success(f"### 预测结论：{res}")
            st.info(f"主队积分: {team_scores[home_team]} | 客队积分: {team_scores[away_team]}")
        else:
            st.warning("⚠️ 未找到该球队，请检查输入是否与数据表中的英文名称完全一致！")
            st.write("数据表中的球队示例:", list(team_scores.keys())[:5])
else:
    st.error("❌ 严重错误：在云端目录下找不到 'EPL_2026.csv'。")
    st.write("请确保：文件已上传到 GitHub 仓库根目录，且拼写为 'EPL_2026.csv'。")
