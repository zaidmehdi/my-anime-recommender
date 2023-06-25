from flask import Flask, render_template, request, redirect, url_for
from anime_similarity import create_df_animelist, calculate_cosine_similarity
from recommender import Recommender
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi



app = Flask(__name__)

def setup_mongodb_client():
    with open('tokens/mongodb_server.txt', 'r') as f:
        url = f.read()
    return MongoClient(url, server_api=ServerApi('1'))

def setup_anime_recommender():
    f = open('tokens/mal_token.json')
    mal_token = json.load(f)

    mongodb_client = setup_mongodb_client()
    df_animelist = create_df_animelist(mongodb_client)
    synopsis_sim = calculate_cosine_similarity(df_animelist, 'synopsis')
    genres_sim = calculate_cosine_similarity(df_animelist, 'genres')

    return Recommender(synopsis_sim, genres_sim, mal_token, mongodb_client, df_animelist)

@app.route('/', methods=['GET', 'POST'])
def home():
    global anime_recommender
    if request.method == 'POST':
        search_term = request.form.get('search')
        user_name_list = str(search_term).split()
        print(user_name_list)
        try:
            recommendations = anime_recommender.recommend(user_name_list)
            return redirect(url_for('rec_results', recommendations = recommendations))
        except Exception as e:
            print(f'Exception in home: {e}')
    
    return render_template('index.html')

@app.route('/rec/<recommendations>')
def rec_results(recommendations):
    print(f'Recommendations: {recommendations}')
    return render_template('rec.html')

if __name__ == '__main__':
    anime_recommender = setup_anime_recommender()
    app.run(debug=True)