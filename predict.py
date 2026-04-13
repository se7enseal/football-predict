import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    # 获取当前代码文件所在的目录
    current_dir = os.path.dirname(__file__)
    # 拼接出 E0.csv 的绝对路径
    file_path = os.path.join(current_dir, 'E0.csv')
    
    # 增加一个检查，如果文件确实没找到，报错会更明确
    if not os.path.exists(file_path):
        st.error(f"找不到文件，请确认 E0.csv 是否在代码同级目录下。当前寻找路径: {file_path}")
        return None
        
    return pd.read_csv(file_path)

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
