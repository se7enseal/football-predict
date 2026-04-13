import streamlit as st
import pandas as pd
import os  # 必须引入 os 模块，这是你之前报错的原因

# --- 1. 数据加载 ---
@st.cache_data
def load_data():
    # 确保文件路径正确指向当前目录下的 EPL_2026.csv
    file_path = os.path.join(os.path.dirname(__file__), 'EPL_2026.csv')
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

# --- 2. 核心分析逻辑 ---
def get_recent_results(df, team):
    # 筛选该队最近5场比赛
    games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(5)
    results = []
    for _, row in games.iterrows():
        is_home = row['HomeTeam'] == team
        # 判断胜平负
        if (is_home and row['FTR']=='H') or (not is_home and row['FTR']=='A'):
            res = "胜"
        elif row['FTR']=='D':
            res = "平"
        else:
            res = "负"
        
        opponent = row['AwayTeam'] if is_home else row['HomeTeam']
        results.append(f"{row['FTHG']}:{row['FTAG']} vs {opponent} ({res})")
    return results

# --- 3. 页面交互 ---
st.title("⚽ 专家级全维度赛果预测系统")
data = load_data()

if data is not None:
    # 获取球队列表（自动去重并排序）
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    col1, col2 = st.columns(2)
    h_name = col1.selectbox("选择主队", teams)
    a_name = col2.selectbox("选择客队", teams)
    
    # 自动展示最近5场战绩（折叠面板，不占空间）
    with st.expander("查看双方近期战绩 (最近5场)"):
        st.write(f"**{h_name}:**", get_recent_results(data, h_name))
        st.write(f"**{a_name}:**", get_recent_results(data, a_name))

    st.sidebar.header("📊 基本面修正")
    h_form = st.sidebar.slider(f"{h_name} 状态 (1-10)", 1, 10, 5)
    a_form = st.sidebar.slider(f"{a_name} 状态 (1-10)", 1, 10, 5)
    
    if st.sidebar.button("生成深度预测"):
        # 获取基础均值
        h_s = data[data['HomeTeam']==h_name]['FTHG'].mean()
        a_s = data[data['AwayTeam']==a_name]['FTAG'].mean()
        
        # 算法模型：基础进球率 * (状态分/5)
        pred_h = int(round(h_s * (h_form/5)))
        pred_a = int(round(a_s * (a_form/5)))
        
        st.subheader(f"📊 预测比分: {pred_h} : {pred_a}")
        
        # 逻辑修复：BTTS 判定
        btts = "是 (Yes)" if (pred_h > 0 and pred_a > 0) else "否 (No)"
        
        st.write(f"**预计总进球:** {pred_h + pred_a} | **双方是否进球 (BTTS):** {btts}")
        
        # 爆冷预警
        if pred_h > 0 and pred_a > 0 and (pred_h + pred_a) < 2:
            st.warning("⚠️ 提示：双边进球但总数极低，比赛可能焦灼。")
else:
    st.error("严重错误：未找到 'EPL_2026.csv'。请确保它已上传至 GitHub 仓库根目录。")
