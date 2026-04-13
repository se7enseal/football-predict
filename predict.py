import streamlit as st
import pandas as pd
import os

# --- 1. 数据与状态逻辑 ---
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

def get_form_score(df, team):
    # 计算近5场比赛积分，并映射到 1-10 分
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    points = 0
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        if (is_home and row['FTR']=='H') or (not is_home and row['FTR']=='A'): points += 3
        elif row['FTR']=='D': points += 1
    # 将 0-15 分映射到 1-10 分区间
    score = int((points / 15) * 9) + 1
    return score

def get_recent_results(df, team):
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    results = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        res = "胜" if (is_home and row['FTR']=='H') or (not is_home and row['FTR']=='A') else ("平" if row['FTR']=='D' else "负")
        results.append(f"{row['FTHG']}:{row['FTAG']} vs {row['AwayTeam'] if is_home else row['HomeTeam']} ({res})")
    return results

# --- 2. 页面布局 ---
st.set_page_config(page_title="足球分析系统", layout="wide")
st.title("⚽ 专家级全维度赛果预测系统")

data = load_data()
if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)
    
    # 自动计算评分
    h_auto_score = get_form_score(data, h_name)
    a_auto_score = get_form_score(data, a_name)
    
    # 滑动条加载自动评分
    st.sidebar.header("📊 基本面修正")
    h_form = st.sidebar.slider(f"{h_name} 状态评分", 1, 10, h_auto_score)
    a_form = st.sidebar.slider(f"{a_name} 状态评分", 1, 10, a_auto_score)
    
    with st.expander("查看双方近期战绩 (自动生成评分来源)"):
        st.write(f"**{h_name} 近况:**", get_recent_results(data, h_name))
        st.write(f"**{a_name} 近况:**", get_recent_results(data, a_name))

    if st.sidebar.button("生成深度预测"):
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        # 预测逻辑
        pred_h = int(round(h_s * (h_form/5)))
        pred_a = int(round(a_s * (a_form/5)))
        
        # 结果展示
        st.subheader(f"📊 预测比分: {pred_h} : {pred_a}")
        st.write(f"**总进球:** {pred_h + pred_a} | **双方是否进球(BTTS):** {'是' if (pred_h > 0 and pred_a > 0) else '否'}")
        
        # 柱状图展示
        st.subheader("📈 攻防战力对比图")
        chart_data = pd.DataFrame({
            "战力指数": [h_s, a_s],
            "分类": ["主队进攻", "客队进攻"]
        }).set_index("分类")
        st.bar_chart(chart_data)
        
        if pred_h > 0 and pred_a > 0 and (pred_h + pred_a) < 2:
            st.warning("⚠️ 提示：双边进球但总数低，比赛可能焦灼。")
else:
    st.error("找不到数据文件，请确认 CSV 路径。")
