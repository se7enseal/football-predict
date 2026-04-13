import streamlit as st
import pandas as pd
import os

# --- 1. 数据加载与处理 ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_team_points(df):
    teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    points = {team: 0 for team in teams}
    for _, row in df.iterrows():
        if row['FTR'] == 'H': points[row['HomeTeam']] += 3
        elif row['FTR'] == 'A': points[row['AwayTeam']] += 3
        else:
            points[row['HomeTeam']] += 1
            points[row['AwayTeam']] += 1
    return points

# --- 2. 新增：计算近期 5 场状态 ---
def get_recent_form(df, team, last_n=5):
    # 筛选该球队参与的最近 N 场比赛
    team_games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(last_n)
    form_score = 0
    for _, row in team_games.iterrows():
        if (row['HomeTeam'] == team and row['FTR'] == 'H') or (row['AwayTeam'] == team and row['FTR'] == 'A'):
            form_score += 3
        elif row['FTR'] == 'D':
            form_score += 1
    return form_score

# --- 3. 页面交互 ---
st.title("⚽ 足球胜负预测：积分+状态模型")
data = load_data()

if data is not None:
    team_scores = get_team_points(data)
    team_names = {name.lower(): name for name in team_scores.keys()}
    
    home_input = st.sidebar.text_input("主队名称").strip().lower()
    away_input = st.sidebar.text_input("客队名称").strip().lower()

    if st.sidebar.button("开始预测"):
        if home_input in team_names and away_input in team_names:
            h_name, a_name = team_names[home_input], team_names[away_input]
            
            # 计算总分 (赛季积分 + 近5场表现)
            h_power = team_scores[h_name] + get_recent_form(data, h_name)
            a_power = team_scores[a_name] + get_recent_form(data, a_name)
            
            diff = h_power - a_power
            
            # 输出离散结论
            if diff > 5: res = f"预测主胜：{h_name} 状态与积分为优"
            elif diff < -5: res = f"预测客胜：{a_name} 状态与积分为优"
            else: res = "势均力敌：平局可能性大"
            
            st.success(f"### {res}")
            st.write(f"数据参考：主队综合分 {h_power} | 客队综合分 {a_power}")
        else:
            st.error("请输入正确的球队名称！")
else:
    st.error("找不到数据文件！")
