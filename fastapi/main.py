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

def load_movies_data_from_db():
    # moviesテーブルからデータを読み込む
    movies_query = 'SELECT * FROM movies'
    movies_data = pd.read_sql(movies_query, engine)
    return movies_data

def load_ratings_data_from_db():
    # ratingsテーブルからデータを読み込む
    ratings_query = 'SELECT * FROM ratings'
    ratings_data = pd.read_sql(ratings_query, engine)
    return ratings_data

# データの読み込み
def load_data_from_db():
    movies_data = load_movies_data_from_db()
    ratings_data = load_ratings_data_from_db()
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

    return top_n_recommendations

def format_output(recommendations, movies_data, k):
    output = []
    for i, (movie_id, score) in enumerate(recommendations.items()):
        title = movies_data[movies_data['movie_id'] == movie_id]['title'].values[0]
        output.append({"number": i+1, "title": title, "recommendation_score": score/k})
    return output

def calculate_item_similarity(ratings_matrix):
    if os.path.exists("item_similarity.npy"):
        item_similarity = np.load("item_similarity.npy")
    else:
        item_similarity = cosine_similarity(ratings_matrix.T)
        np.save("item_similarity.npy", item_similarity)
    return item_similarity

def recommend_items(item_id, item_similarity_matrix, movie_titles, n=5):
    similar_items = pd.Series(item_similarity_matrix[item_id]).sort_values(ascending=False)[1:n+1]
    recommended_items = []
    for i, (idx, similarity) in enumerate(similar_items.items(), 1):
        movie_id = movie_titles.index[idx]
        recommended_items.append({
            "number": i,
            "title": movie_titles.loc[movie_id],
            "similarity": similarity,
        })
    return recommended_items

# APIのエンドポイント
@app.get('/recommendations/userbase')
def userbase_recommendations(user_id: int = Query(1, description="The user ID"), n: int = Query(5, description="Number of recommendations"), k: int = Query(10, description="Number of similar users")):
    # データの読み込み
    movies_data, ratings_data = load_data_from_db()

    # データの前処理
    merged_df = preprocess_data(movies_data, ratings_data)

    # 推薦の取得
    recommendations = get_recommendations(merged_df, user_id, n, k)

    output = format_output(recommendations, movies_data, k)

    return output

# APIのエンドポイント
@app.get('/recommendations/itembase')
def itembase_recommendations(movie_id: int = Query(1, description="The Movie ID"), n: int = Query(5, description="Number of recommendations")):
    # 類似度行列のファイルが存在すれば読み込む
    if os.path.exists("item_similarity.npy"):
        item_similarity = np.load("item_similarity.npy")
    # ファイルが存在しなければ作成する
    else:
        ratings_df = load_ratings_data_from_db()
        ratings_matrix = ratings_df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
        item_similarity = calculate_item_similarity(ratings_matrix)

    # レーティングデータを読み込む
    movies_df = load_movies_data_from_db()
    movie_titles = movies_df.set_index("movie_id")["title"]
    # 例として、アイテムIDが1の映画に対する推薦を行う
    recommended_items = recommend_items(movie_id, item_similarity, movie_titles, n)

    return recommended_items
