import os
from fastapi import FastAPI, Query
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# データベース接続設定
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# データの読み込み
def load_data_from_db():
    # moviesテーブルからデータを読み込む
    movies_query = 'SELECT * FROM movies'
    movies_data = pd.read_sql(movies_query, engine)

    # ratingsテーブルからデータを読み込む
    ratings_query = 'SELECT * FROM ratings'
    ratings_data = pd.read_sql(ratings_query, engine)

    return movies_data, ratings_data

# データの前処理
def preprocess_data(movies_data, ratings_data):
    # 必要な前処理を実行する
    merged_df = pd.merge(ratings_data, movies_data, on='movie_id')
    genre_split = merged_df['genres'].str.get_dummies()
    genre_split.columns = ['genre_' + column for column in genre_split.columns]
    merged_df = merged_df.drop(['title', 'genres'], axis=1)
    merged_df = pd.concat([merged_df, genre_split], axis=1)

    return merged_df

# 推薦の取得
def get_recommendations(df: pd.DataFrame, user_id: int, n: int = 5, k: int = 10):
    user_movie_matrix = df.pivot_table(index='user_id', columns='movie_id', values='rating')
    user_similarity = cosine_similarity(user_movie_matrix.fillna(0))
    
    # 指定されたユーザーの評価を取得
    user_ratings = user_movie_matrix.loc[user_id].fillna(0)
    
    # ユーザーの平均評価を計算
    mean_user_rating = user_ratings.mean()
    
    # 類似ユーザーのインデックスを取得
    similar_users_idx = np.argsort(user_similarity[user_id])[::-1][1:k+1]  # ユーザー自身は除外
    
    # 類似ユーザーの評価を取得
    similar_users_ratings = user_movie_matrix.iloc[similar_users_idx].fillna(0)
    
    # 対象ユーザーがまだ見ていないアイテムを抽出
    unseen_items = (user_ratings == 0)
    
    # 類似ユーザーが高評価をつけたアイテムを抽出
    high_rated_items = (similar_users_ratings > mean_user_rating)
    
    # 対象ユーザーがまだ見ていないかつ類似ユーザーが高評価をつけたアイテムを抽出
    recommended_items = (high_rated_items & unseen_items)
    
    # 推薦アイテムの高評価度と類似度の積を計算
    recommendation_scores = recommended_items.mul(user_similarity[user_id][similar_users_idx], axis=0).sum(axis=0)
    
    # 上位n個のアイテムを抽出して返す
    top_n_recommendations = recommendation_scores.sort_values(ascending=False).head(n)

    # output = [{"number": i+1, "movie_id": idx, "recommendation_score": score/k} for i, (idx, score) in enumerate(top_n_recommendations.items())]
    
    return top_n_recommendations

def format_output(recommendations, movies_data, k):
    output = []
    for i, (movie_id, score) in enumerate(recommendations.items()):
        title = movies_data[movies_data['movie_id'] == movie_id]['title'].values[0]
        output.append({"number": i+1, "title": title, "recommendation_score": score/k})
    return output

# APIのエンドポイント
@app.get('/recommendations')
def recommendations(user_id: int = Query(1, description="The user ID"), n: int = Query(5, description="Number of recommendations"), k: int = Query(10, description="Number of similar users")):
    # データの読み込み
    movies_data, ratings_data = load_data_from_db()

    # データの前処理
    merged_df = preprocess_data(movies_data, ratings_data)

    # 推薦の取得
    recommendations = get_recommendations(merged_df, user_id, n, k)

    output = format_output(recommendations, movies_data, k)

    return output
