import streamlit as st
import numpy as np
import pandas as pd
import copy

def simulate_oripa(packs_total, cost_per_pack, top_prize_value, guaranteed_value, additional_prizes, simulations=10):
    def simulate_once(prizes):
        # プールの初期化
        pool = [1]  # 1はTOP賞として予約
        pool += [draw for draw, info in prizes.items() for _ in range(info['count'])]  # 追加の当たり賞
        pool += [0] * (packs_total - len(pool))  # 残りを外れにする
        np.random.shuffle(pool)  # プールをシャッフル
        trials = 0
        prize_value = 0
        history = []
        
        while True:
            trials += 1
            draw = pool.pop()  # パックを引く
            if draw == 1:  # TOP賞が1と仮定
                prize_value += top_prize_value
                history.append((trials, "TOP賞", top_prize_value))
                break
            elif draw != 0:  # 追加の当たり賞
                prize_value += prizes[draw]['value']
                history.append((trials, f"追加の当たり賞 ({draw})", prizes[draw]['value']))
            else:  # 外れ
                history.append((trials, "外れ", 0))

        total_cost = trials * cost_per_pack
        guaranteed_return = (trials - 1) * guaranteed_value
        net_cost = total_cost - guaranteed_return - prize_value
        return trials, total_cost, guaranteed_return + prize_value, net_cost, history

    results = [simulate_once(copy.deepcopy(additional_prizes)) for _ in range(simulations)]
    return results

# Streamlitアプリケーションの作成
st.title("オリパシミュレーションツール")

# ユーザー入力
packs_total = st.number_input("パックの総数", value=39, min_value=1)
cost_per_pack = st.number_input("1パックのコスト", value=1000, min_value=1)
top_prize_value = st.number_input("TOP賞の価値", value=13000, min_value=1)
guaranteed_value = st.number_input("保証されるリターンの価値", value=500, min_value=0)
simulations = st.number_input("シミュレーション回数", value=10, min_value=1)

# 追加の当たり賞
additional_prizes = {}
num_prizes = st.number_input("追加の当たり賞の数", value=1, min_value=1)

for i in range(num_prizes):
    cols = st.columns(3)
    with cols[0]:
        key = st.number_input(f"番号 {i+1}", value=2, min_value=1, key=f'key_{i}')
    with cols[1]:
        value = st.number_input(f"価値 {i+1}", value=5000, min_value=1, key=f'value_{i}')
    with cols[2]:
        count = st.number_input(f"枚数 {i+1}", value=1, min_value=1, key=f'count_{i}')
    additional_prizes[key] = {'value': value, 'count': count}

if st.button("シミュレーション実行"):
    simulation_results = simulate_oripa(packs_total, cost_per_pack, top_prize_value, guaranteed_value, additional_prizes, simulations)

    # 結果をデータフレームに変換
    df_results = pd.DataFrame(
        [(result[0], result[1], result[2], result[3]) for result in simulation_results], 
        columns=['試行回数', '合計コスト', '保証されたリターン + 賞金', '実質コスト']
    )

    # データフレームを表示
    st.write("シミュレーション結果", df_results)

    # 結果のまとめ
    average_trials = np.mean(df_results['試行回数'])
    average_total_cost = np.mean(df_results['合計コスト'])
    average_guaranteed_return = np.mean(df_results['保証されたリターン + 賞金'])
    average_net_cost = np.mean(df_results['実質コスト'])

    st.write(f"\n平均試行回数: {average_trials}")
    st.write(f"平均合計コスト: {average_total_cost}")
    st.write(f"平均保証リターン + 賞金: {average_guaranteed_return}")
    st.write(f"平均実質コスト: {average_net_cost}")

    if average_net_cost < 0:
        st.write("結果: 利益")
    else:
        st.write("結果: 損失")

    # 各シミュレーションの詳細を表示
    for i, result in enumerate(simulation_results):
        with st.expander(f"シミュレーション {i+1} の詳細"):
            st.write(f"試行回数: {result[0]}")
            st.write(f"合計コスト: {result[1]}")
            st.write(f"保証されたリターン + 賞金: {result[2]}")
            st.write(f"実質コスト: {result[3]}")
            history_df = pd.DataFrame(result[4], columns=['試行回', '結果', '価値'])
            st.write("履歴", history_df)
