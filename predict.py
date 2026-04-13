import pandas as pd

# 1. 加载数据 (假设你的文件名是 E0.csv)
file_path = 'E0.csv' 
data = pd.read_csv(file_path)

# 2. 简易实力建模：我们用“积分”来代表离散的实力分
def get_team_points(df):
    teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    points = {team: 0 for team in teams}
    
    for _, row in df.iterrows():
        if row['FTR'] == 'H': # 主胜
            points[row['HomeTeam']] += 3
        elif row['FTR'] == 'A': # 客胜
            points[row['AwayTeam']] += 3
        else: # 平局
            points[row['HomeTeam']] += 1
            points[row['AwayTeam']] += 1
    return points

# 获取全联赛当前积分
team_scores = get_team_points(data)

# 3. 胜负预测逻辑
def predict(home_team, away_team, scores):
    h_p = scores.get(home_team, 0)
    a_p = scores.get(away_team, 0)
    
    # 离散差值计算
    diff = h_p - a_p
    
    print(f"【{home_team} vs {away_team}】")
    print(f" 积分差距: {diff}")
    
    if diff > 10:
        return "预测结果：主胜 (实力碾压)"
    elif diff < -10:
        return "预测结果：客胜 (客队强势)"
    else:
        return "预测结果：平局或小球 (双方势均力敌)"

# 4. 测试一下：输入你想预测的下一场对阵
print(predict('Arsenal', 'Everton', team_scores))