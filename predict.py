import streamlit as st
import pandas as pd
import os

# --- 1. 数据加载 ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'EPL_2026.csv')
    return pd.read_csv(file_path) if os.path.exists(file_path) else None

# --- 2. 统计逻辑 ---
def get_detailed_stats(df, team):
    home_games = df[df['HomeTeam'] == team]
    away_games = df[df['AwayTeam'] == team]
    
    # 场均进球与失球
    h_s = home_games['FTHG'].mean() if not home_games.empty else 0
    h_c = home_games['FTAG'].mean() if not home_games.empty else 0
    a_s = away_games['FTAG'].mean() if not away_games.empty else 0
    a_c = away_games['FTHG'].mean() if not away_games.empty else 0
    
    return h_s, h_c, a_s, a_c

# --- 3. 页面布局 ---
st.set_page_config(page_title="足球大数据分析终端", layout="wide")
st.title("⚽ 专家级全维度赛果预测系统")

data = load_data()

if data is not None:
    teams = sorted(list(set(data['HomeTeam']) | set(data['AwayTeam'])))
    
    # 侧边栏：基本面手动调节
    st.sidebar.header("📊 基本面实时修正")
    h_name = st.sidebar.selectbox("选择主队", teams, index=0)
    h_form = st.sidebar.slider(f"{h_name} 近期状态得分", 1, 10, 5)
    
    st.sidebar.markdown("---")
    a_name = st.sidebar.selectbox("选择客队", teams, index=1)
    a_form = st.sidebar.slider(f"{a_name} 近期状态得分", 1, 10, 5)
    
    if st.sidebar.button("生成深度分析报告"):
        # 获取基础数据
        h_s, h_c, _, _ = get_detailed_stats(data, h_name)
        _, _, a_s, a_c = get_detailed_stats(data, a_name)
        
        # 4. 预测算法（核心优化：加入状态权重修正进球期望值）
        # 逻辑：基础进球期望 * (状态分/5)
        exp_h = ((h_s + a_c) / 2) * (h_form / 5)
        exp_a = ((a_s + h_c) / 2) * (a_form / 5)
        
        pred_h = int(round(exp_h))
        pred_a = int(round(exp_a))
        
        # 5. 结果展示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("核心预测比分", f"{pred_h} : {pred_a}")
        with col2:
            st.metric("预计总进球", f"{pred_h + pred_a} 球")
        with col3:
            btts = "是 (Yes)" if (exp_h > 0.8 and exp_a > 0.8) else "否 (No)"
            st.metric("双方是否得分", btts)
            
        # 6. 可视化图表
        st.subheader("📈 攻防战力对比图")
        chart_data = pd.DataFrame({
            "战力指数": [h_s, h_c, a_s, a_c],
            "分类": ["主队场均进球", "主队场均失球", "客队场均进球", "客队场均失球"]
        }).set_index("分类")
        st.bar_chart(chart_data)
        
        # 7. 爆冷预警逻辑
        st.subheader("💡 专家建议")
        diff = (h_form + h_s*2) - (a_form + a_s*2)
        if abs(diff) < 2:
            st.warning("⚠️ 双方纸面实力与近况极度接近，建议首选平局。")
        elif h_form < 4 and h_s > a_s:
            st.error(f"❗ 警报：{h_name} 虽然赛季数据好，但近期状态滑坡，防爆冷。")
        else:
            winner = h_name if exp_h > exp_a else a_name
            st.success(f"✅ 模型更倾向于看好 {winner} 保持不败或取胜。")
else:
    st.error("无法加载 EPL_2026.csv，请检查文件是否在 GitHub 根目录。")
