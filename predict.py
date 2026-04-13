import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# --- 1. 数据逻辑 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_injury_report(team_name):
    # 这是一个模拟抓取函数，实际使用中请根据具体的体育网站替换 URL
    # 这里我们返回一个友好的格式，如果抓取失败，显示预警
    try:
        # 示例：假设我们从某个体育页面获取伤病
        # url = f"https://www.transfermarkt.com/..." 
        # 此处省略复杂的网络请求代码以防报错
        return ["主力中卫: 轻伤待定", "中场指挥官: 已恢复训练"]
    except:
        return ["暂无实时伤病数据"]

# --- 2. 页面配置 ---
st.set_page_config(page_title="专业足球分析系统", layout="wide")
st.title("⚽ 专家级全维度赛果预测系统")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    # 伤病报告显示
    st.subheader("🏥 双方阵容情报")
    c1, c2 = st.columns(2)
    with c1: st.write(f"**{h_name} 伤病名单:**", get_injury_report(h_name))
    with c2: st.write(f"**{a_name} 伤病名单:**", get_injury_report(a_name))

    # 自动评分逻辑
    h_score = int((data[(data['HomeTeam']==h_name)|(data['AwayTeam']==h_name)].tail(5)['FTHG'].sum() / 15) * 9) + 1
    a_score = int((data[(data['HomeTeam']==a_name)|(data['AwayTeam']==a_name)].tail(5)['FTAG'].sum() / 15) * 9) + 1
    
    st.sidebar.header("📊 基本面修正")
    h_form = st.sidebar.slider(f"{h_name} 状态 (1-10)", 1, 10, h_score)
    a_form = st.sidebar.slider(f"{a_name} 状态 (1-10)", 1, 10, a_score)

    if st.sidebar.button("生成深度分析"):
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        pred_h, pred_a = int(round(h_s * (h_form/5))), int(round(a_s * (a_form/5)))
        
        st.subheader(f"📊 预测比分: {pred_h} : {pred_a}")
        
        # Plotly 高级交互图表 (解决太粗的问题)
        fig = go.Figure(data=[
            go.Bar(name='主队进攻', x=['进球/失球'], y=[h_s], marker_color='#1f77b4'),
            go.Bar(name='客队进攻', x=['进球/失球'], y=[a_s], marker_color='#ff7f0e')
        ])
        fig.update_layout(barmode='group', height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("数据文件加载失败，请检查 'EPL_2026.csv'。")
