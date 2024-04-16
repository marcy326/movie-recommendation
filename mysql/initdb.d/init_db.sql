-- moviesテーブルの作成と初期データの挿入
CREATE TABLE IF NOT EXISTS movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255) NOT NULL
);

-- ratingsテーブルの作成と初期データの挿入
CREATE TABLE IF NOT EXISTS ratings (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating FLOAT NOT NULL,
    timestmp INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- moviesテーブルに初期データを挿入
-- moviesテーブルに初期データを挿入するクエリの実行開始ログを出力
SELECT 'Inserting initial data into movies table...' AS 'Log';

LOAD DATA LOCAL INFILE '/data/movies.csv' 
INTO TABLE movies 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;

-- moviesテーブルに初期データを挿入するクエリの実行終了ログを出力
SELECT 'Initial data inserted into movies table successfully.' AS 'Log';

-- ratingsテーブルに初期データを挿入
-- ratingsテーブルに初期データを挿入するクエリの実行開始ログを出力
SELECT 'Inserting initial data into ratings table...' AS 'Log';

LOAD DATA LOCAL INFILE '/data/ratings.csv' 
INTO TABLE ratings 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;

-- ratingsテーブルに初期データを挿入するクエリの実行終了ログを出力
SELECT 'Initial data inserted into ratings table successfully.' AS 'Log';
