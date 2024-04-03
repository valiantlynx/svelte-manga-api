import lancedb

import numpy as np
import pandas as pd
from main import get_recommendations, data
import main

# TESTING ======================================================


def test_main():
    ratings = pd.read_csv('./manga-data/ratings.csv', header=None,
                          names=["user id", "manga id", "rating", "timestamp"])
    ratings = ratings.drop(columns=['timestamp'])
    ratings = ratings.drop(0)
    ratings["rating"] = ratings["rating"].values.astype(np.float32)
    ratings["user id"] = ratings["user id"].values.astype(np.int32)
    ratings["manga id"] = ratings["manga id"].values.astype(np.int32)

    reviewmatrix = ratings.pivot(
        index="user id", columns="manga id", values="rating").fillna(0)

    # SVD
    matrix = reviewmatrix.values
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)

    vectors = np.rot90(np.fliplr(vh))
    print(vectors.shape)

    # Metadata
    mangas = pd.read_csv('./manga-data/mangas.csv', header=0,
                         names=["manga id", "title", "genres"])
    mangas = mangas[mangas['manga id'].isin(reviewmatrix.columns)]

    for i in range(len(mangas)):
        data.append({"id": mangas.iloc[i]["manga id"], "title": mangas.iloc[i]
                    ['title'], "vector": vectors[i], "genre": mangas.iloc[i]['genres']})
    print(pd.DataFrame(data))

    # Connect to LanceDB

    db = lancedb.connect("./data/test-db")
    try:
        main.table = db.create_table("manga_set", data=data)
    except:
        main.table = db.open_table("manga_set")

    print(get_recommendations("Moana (2016)"))
    print(get_recommendations("Rogue One: A Star Wars Story (2016)"))
