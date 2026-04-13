import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# --- 1. 数据逻辑 ---
@st.cache_data
def load_all_data():
    df = pd.read_csv('EPL_2026.csv') if os.path.exists('EPL_2026.csv') else None
    cfg = pd.read_csv('match_config.csv') if os.path.exists('match_config.csv') else None
    return df, cfg

# --- 2. 界面与交互 ---
st.set_page_config(page_title="足球专家雷达分析系统", layout="wide")
st.title("⚽ 专家级多维度赛果预测终端")

data, cfg = load_all_data()

if data is not None and cfg is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)

    # 提取雷达图维度
    def get_metrics(team_name):
        row = cfg[cfg['Team'] == team_name]
        if not row.empty:
            return row.iloc[0, 1:].to_dict() # 假设从第2列开始是维度数据
        return {"进攻": 5, "防守": 5, "近期状态": 5, "战术克制": 5, "伤病影响": 5, "积分排名": 5}

    h_metrics = get_metrics(h_name)
    a_metrics = get_metrics(a_name)

    # 雷达图绘制
    st.subheader("📊 战力多维雷达图")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(h_metrics.values()), theta=list(h_metrics.keys()), fill='toself', name=h_name))
    fig.add_trace(go.Scatterpolar(r=list(a_metrics.values()), theta=list(a_metrics.keys()), fill='toself', name=a_name))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 自动评分作为滑动条基准
    h_init = int(np.mean(list(h_metrics.values())))
    a_init = int(np.mean(list(a_metrics.values())))

    st.sidebar.header("📊 权重修正")
    h_form = st.sidebar.slider(f"{h_name} 最终状态分", 1, 10, h_init)
    a_form = st.sidebar.slider(f"{a_name} 最终状态分", 1, 10, a_init)

    if st.sidebar.button("生成最终结论"):
        # 基础数据
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        # 预测模型
        pred_h = int(round(h_s * (h_form/5)))
        pred_a = int(round(a_s * (a_form/5)))
        
        st.markdown("---")
        st.subheader(f"🎯 预测比分: {pred_h} : {pred_a}")
        st.write(f"**预计总进球:** {pred_h + pred_a} | **双方是否进球(BTTS):** {'是' if (pred_h > 0 and pred_a > 0) else '否'}")
        
        st.success(f"根据雷达图综合战力与基本面修正，本场比赛 {h_name} 的胜率为 {int((h_form/(h_form+a_form))*100)}%。")
else:
    st.error("请检查 EPL_2026.csv 与 match_config.csv 是否存在。")
