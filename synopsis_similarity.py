import json
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib


def create_df_animelist():
    global animelist

    response = animelist.find()
    id_list = []
    rating_list = []
    synopsis_list = []
    type_list = []

    for anime in response:
        if 'mean' in anime and 'synopsis' in anime and 'media_type' in anime:
            id_list.append(anime['_id'])
            rating_list.append(anime['mean'])
            synopsis_list.append(anime['synopsis'])
            type_list.append(anime['media_type'])

    df_animelist = pd.DataFrame({'id': id_list, 'rating': rating_list, 'synopsis': synopsis_list, 'type': type_list})
    df_animelist = df_animelist[df_animelist.type == 'tv' ]

    return df_animelist

def cosine_similarity(df_animelist):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_animelist['synopsis'])

    synopsis_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    joblib.dump(synopsis_sim, 'synopsis_sim.pkl')

    return synopsis_sim


if __name__ == "__main__":
    f = open('setup/token.json')
    token = json.load(f)

    CONNECTION_STRING = ""
    client = MongoClient(CONNECTION_STRING)
    dbname = client['MAL']
    animelist = dbname['animelist']

    df_animelist = create_df_animelist()
    synopsis_sim = cosine_similarity(df_animelist)



