import lancedb

import numpy as np
import pandas as pd
import pytest
import subprocess
from main import get_recommendations, data
import main

# DOWNLOAD ======================================================

subprocess.Popen("curl https://files.grouplens.org/datasets/movielens/movie-data.zip -o movie-data.zip", shell=True).wait()
subprocess.Popen("unzip movie-data.zip", shell=True).wait()

# TESTING ======================================================


def test_main():
    ratings = pd.read_csv('./movie-data/ratings.csv', header=None, names=["user id", "movie id", "rating", "timestamp"])
    ratings = ratings.drop(columns=['timestamp'])
    ratings = ratings.drop(0)
    ratings["rating"] = ratings["rating"].values.astype(np.float32)
    ratings["user id"] = ratings["user id"].values.astype(np.int32)
    ratings["movie id"] = ratings["movie id"].values.astype(np.int32)

    reviewmatrix = ratings.pivot(index="user id", columns="movie id", values="rating").fillna(0)

    # SVD
    matrix = reviewmatrix.values
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)

    vectors = np.rot90(np.fliplr(vh))
    print(vectors.shape)


    # Metadata
    movies = pd.read_csv('./movie-data/movies.csv', header=0, names=["movie id", "title", "genres"])
    movies = movies[movies['movie id'].isin(reviewmatrix.columns)]

    for i in range(len(movies)):
        data.append({"id": movies.iloc[i]["movie id"], "title": movies.iloc[i]['title'], "vector": vectors[i], "genre": movies.iloc[i]['genres']})
    print(pd.DataFrame(data))


    # Connect to LanceDB

    db = lancedb.connect("./data/test-db")
    try:
        main.table = db.create_table("movie_set", data=data)
    except:
        main.table = db.open_table("movie_set")


    print(get_recommendations("Moana (2016)"))
    print(get_recommendations("Rogue One: A Star Wars Story (2016)"))