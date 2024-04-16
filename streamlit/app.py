import os
import time
import streamlit as st
import pandas as pd
import requests

# API エンドポイントの URL
API_URL = os.getenv("API_URL")

def get_recommendations(user_id, n, k):
    # API を呼び出して推薦結果を取得
    params = {"user_id": user_id, "n": n, "k": k}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Streamlit アプリのインターフェースを作成
def main():
    st.title("Movie Recommendations")
    st.write("Enter user ID to get movie recommendations:")

    # ユーザーIDを入力
    user_id = st.number_input("User ID", value=1, step=1)

    # 推薦数と類似ユーザー数を選択
    n = st.number_input("Number of recommendations", value=5, step=1)
    k = st.number_input("Number of similar users", value=10, step=1)

    # 推薦を取得
    if st.button("Get Recommendations"):
        start_time = time.time()
        recommendations = get_recommendations(user_id, n, k)
        recommendations_table = pd.DataFrame(recommendations).set_index("number")
        if recommendations:
            st.write("Top Recommendations:")
            st.table(recommendations_table)
            # for i, rec in enumerate(recommendations, start=1):
            #     # title = get_title(rec['movie_id'])
            #     st.write(f"{i}. {rec['title']}, Recommendation Score: {rec['recommendation_score']:.2f}")
        else:
            st.error("Failed to get recommendations.")
        end_time = time.time()
        st.write(f"{end_time - start_time:.2f}sec")

if __name__ == "__main__":
    main()
