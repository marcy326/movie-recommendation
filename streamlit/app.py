import os
import time
import streamlit as st
import pandas as pd
import requests

# API エンドポイントの URL
USERBASE_API_URL = os.getenv("USERBASE_API_URL")
ITEMBASE_API_URL = os.getenv("ITEMBASE_API_URL")

def get_userbase_api(user_id, n, k):
    # API を呼び出して推薦結果を取得
    params = {"user_id": user_id, "n": n, "k": k}
    response = requests.get(USERBASE_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_itembase_api(user_id, n):
    # API を呼び出して推薦結果を取得
    params = {"movie_id": user_id, "n": n}
    response = requests.get(ITEMBASE_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Streamlit アプリのインターフェースを作成
def userbase_recommendation():
    st.title("Movie Recommendations")
    st.write("Enter user ID to get movie recommendations:")

    # ユーザーIDを入力
    user_id = st.number_input("User ID", value=1, step=1)

    # 推薦数と類似ユーザー数を選択
    n = st.number_input("Number of recommendations", value=5, step=1, key="userbase-n")
    k = st.number_input("Number of similar users", value=10, step=1)

    # 推薦を取得
    if st.button("Get Recommendations", key="userbase-recommendation"):
        start_time = time.time()
        recommendations = get_userbase_api(user_id, n, k)
        recommendations_table = pd.DataFrame(recommendations).set_index("number")
        if recommendations:
            st.write("Top Recommendations:")
            st.table(recommendations_table)
        else:
            st.error("Failed to get recommendations.")
        end_time = time.time()
        st.write(f"{end_time - start_time:.2f}sec")

def itembase_recommendation():
    st.title("Movie Recommendations")
    st.write("Enter user ID to get movie recommendations:")

    # ユーザーIDを入力
    movie_id = st.number_input("Movie ID", value=1, step=1)

    # 推薦数と類似ユーザー数を選択
    n = st.number_input("Number of recommendations", value=5, step=1, key="itembase-n")

    # 推薦を取得
    if st.button("Get Recommendations", key="itembase-recommendation"):
        start_time = time.time()
        recommendations = get_itembase_api(movie_id, n)
        recommendations_table = pd.DataFrame(recommendations).set_index("number")
        if recommendations:
            st.write("Top Recommendations:")
            st.table(recommendations_table)
        else:
            st.error("Failed to get recommendations.")
        end_time = time.time()
        st.write(f"{end_time - start_time:.2f}sec")

def main():
    tab1, tab2 = st.tabs(["user-base", "item-base"])
    with tab1:
        userbase_recommendation()
    with tab2:
        itembase_recommendation()

if __name__ == "__main__":
    main()
