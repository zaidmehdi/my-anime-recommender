from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib


def create_df_animelist(mongodb_client):
    dbname = mongodb_client['MAL']
    animelist = dbname['animelist']

    response = animelist.find()
    id_list = []
    rating_list = []
    synopsis_list = []
    type_list = []
    genres_list = []

    for anime in response:
        if 'mean' in anime and 'synopsis' in anime and 'media_type' in anime and 'genres' in anime:
            id_list.append(anime['_id'])
            rating_list.append(anime['mean'])
            synopsis_list.append(anime['synopsis'])
            type_list.append(anime['media_type'])
            anime_genres = anime['genres']
            anime_genres_string = ""
            for genre in anime_genres:
                anime_genres_string += f"{genre['name']} "
            genres_list.append(anime_genres_string.strip())

    df_animelist = pd.DataFrame({'id': id_list, 'rating': rating_list, 'synopsis': synopsis_list, 'type': type_list, 'genres': genres_list})
    df_animelist = df_animelist[df_animelist.type == 'tv' ]

    return df_animelist

def calculate_cosine_similarity(df_animelist, column_name: str):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_animelist[column_name])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return cosine_sim


if __name__ == "__main__":

    with open('mongodb_server.txt', 'r') as f:
        CONNECTION_STRING = f.read()
    client = MongoClient(CONNECTION_STRING)
    dbname = client['MAL']
    animelist = dbname['animelist']

    df_animelist = create_df_animelist()
    synopsis_sim = calculate_cosine_similarity(df_animelist, 'synopsis')
    genres_sim = calculate_cosine_similarity(df_animelist, 'genres')

    df_animelist.to_csv('df_animelist.csv', index=False)
    joblib.dump(synopsis_sim, 'synopsis_sim.pkl')
    joblib.dump(genres_sim, 'genres_sim.pkl')



