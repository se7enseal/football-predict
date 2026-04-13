import streamlit as st
import pandas as pd

# 1. --- 数据加载区 (只运行一次) ---
@st.cache_data  # 这个装饰器能让网页加载更快
def load_data():
    df = pd.read_csv('E0.csv')
    return df

data = load_data()

# --- 你的原始积分逻辑 ---
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

team_scores = get_team_points(data)

# 2. --- 预测逻辑函数 ---
def predict(home_team, away_team, scores):
    h_p = scores.get(home_team, 0)
    a_p = scores.get(away_team, 0)
    diff = h_p - a_p
    if diff > 10: return "主胜 (实力碾压)"
    elif diff < -10: return "客胜 (客队强势)"
    else: return "平局或小球 (双方势均力敌)"

# 3. --- 网页 UI 交互区 (网页的核心展示) ---
st.title("⚽ 足球赛果智能预测系统")

# 侧边栏输入
home_team = st.sidebar.text_input("输入主队名称 (如: Arsenal)")
away_team = st.sidebar.text_input("输入客队名称 (如: Everton)")

# 点击按钮触发
if st.sidebar.button("开始预测"):
    if home_team in team_scores and away_team in team_scores:
        result = predict(home_team, away_team, team_scores)
        st.success(f"### 预测结果：{result}")
    else:
        st.error("球队名称未找到，请检查拼写是否与 CSV 数据一致！")

# 4. --- 额外展示区 (让页面更丰富) ---
st.write("---")
st.write("当前积分榜预览：")
st.dataframe(pd.DataFrame.from_dict(team_scores, orient='index', columns=['积分']))
