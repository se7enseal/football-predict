import streamlit as st
import pandas as pd
import numpy as np

# --- 1. 数据处理 ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv('EPL_2026.csv')
    except:
        return None

# --- 2. 网页 UI ---
st.set_page_config(page_title="足球分析专家", layout="wide")
st.title("⚽ 足球专家级综合分析系统")

data = load_data()

if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    # 左右布局
    col_l, col_r = st.columns(2)
    h_name = col_l.selectbox("选择主队", teams)
    a_name = col_r.selectbox("选择客队", teams)
    
    # 基本面输入
    st.sidebar.header("基本面修正")
    h_form = st.sidebar.slider(f"{h_name} 状态 (1-10)", 1, 10, 7)
    a_form = st.sidebar.slider(f"{a_name} 状态 (1-10)", 1, 10, 7)
    
    if st.button("生成详细分析报告"):
        # 计算核心数据
        home_df = data[data['HomeTeam'] == h_name]
        away_df = data[data['AwayTeam'] == a_name]
        
        h_goal_avg = home_df['FTHG'].mean()
        a_goal_avg = away_df['FTAG'].mean()
        
        # 可视化：攻防趋势图
        st.subheader("📊 攻防效率趋势")
        chart_data = pd.DataFrame({
            '进攻效率': [h_goal_avg, a_goal_avg],
            '近期状态': [h_form/10, a_form/10]
        }, index=[h_name, a_name])
        st.bar_chart(chart_data)
        
        # 详细文字报告
        st.subheader("📝 专家洞察")
        st.write(f"根据赛季数据，**{h_name}** 在主场平均能打入 {h_goal_avg:.2f} 球。")
        st.write(f"结合状态评分，模型显示本场比赛的进球期望值为 {h_goal_avg + a_goal_avg:.2f}。")
        
        # 最终预测
        if h_form > a_form + 2:
            st.success(f"结论：{h_name} 状态更佳，主场具备拿分优势。")
        elif a_form > h_form + 2:
            st.warning(f"结论：{a_name} 客场反击效率高，建议关注冷门。")
        else:
            st.info("结论：双方势均力敌，平局概率较高。")
            
else:
    st.error("数据加载失败，请检查 CSV 文件名是否为 'EPL_2026.csv'。")
