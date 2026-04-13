import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv('EPL_2026.csv') if os.path.exists('EPL_2026.csv') else None

def get_recent_results(df, team):
    # 筛选该队最近5场
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    results = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        res = "胜" if (is_home and row['FTR']=='H') or (not is_home and row['FTR']=='A') else ("平" if row['FTR']=='D' else "负")
        opponent = row['AwayTeam'] if is_home else row['HomeTeam']
        results.append(f"{row['FTHG']}:{row['FTAG']} vs {opponent} ({res})")
    return results

st.title("⚽ 专家级全维度赛果预测系统")
data = load_data()

if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)
    
    # 自动展示最近5场战绩
    with st.expander("查看双方近期战绩 (最近5场)"):
        st.write(f"**{h_name}:**", get_recent_results(data, h_name))
        st.write(f"**{a_name}:**", get_recent_results(data, a_name))

    st.sidebar.header("📊 基本面修正")
    h_form = st.sidebar.slider(f"{h_name} 状态 (1-10)", 1, 10, 5)
    a_form = st.sidebar.slider(f"{a_name} 状态 (1-10)", 1, 10, 5)
    
    if st.sidebar.button("生成分析"):
        # 简化计算模型
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        pred_h = int(round(h_s * (h_form/5)))
        pred_a = int(round(a_s * (a_form/5)))
        
        # 修正后的展示逻辑
        st.subheader(f"📊 预测比分: {pred_h} : {pred_a}")
        st.write(f"**预计总进球:** {pred_h + pred_a} | **双方是否进球:** {'是' if (pred_h > 0 and pred_a > 0) else '否'}")
        
        # 逻辑预警
        if pred_h > 0 and pred_a > 0 and (pred_h + pred_a) < 2:
            st.warning("⚠️ 提示：双边进球但总数极低，注意防平。")
else:
    st.error("请确保 EPL_2026.csv 在仓库根目录。")
