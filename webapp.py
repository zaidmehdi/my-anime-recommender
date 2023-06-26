from flask import Flask, render_template, request, redirect, url_for, session
from anime_similarity import create_df_animelist, calculate_cosine_similarity
from recommender import Recommender
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi


app = Flask(__name__)
app.secret_key = 'test'

def setup_mongodb_client():
    with open('tokens/mongodb_server.txt', 'r') as f:
        url = f.read()
    return MongoClient(url, server_api=ServerApi('1'))

def setup_anime_recommender():
    global mongodb_client
    f = open('tokens/mal_token.json')
    mal_token = json.load(f)

    df_animelist = create_df_animelist(mongodb_client)
    synopsis_sim = calculate_cosine_similarity(df_animelist, 'synopsis')
    genres_sim = calculate_cosine_similarity(df_animelist, 'genres')

    return Recommender(synopsis_sim, genres_sim, mal_token, mongodb_client, df_animelist)

def get_anime_info(anime_id):
    global mongodb_client
    dbname = mongodb_client['MAL']
    anime_data = dbname['animelist']

    anime_info = {}
    response = anime_data.find({"_id": anime_id})
    anime_dict = next(response, None)
    if anime_dict:
        anime_info['id'] = anime_id
        anime_info['title'] = anime_dict['title']
        anime_info['picture'] = anime_dict['main_picture']['medium']
    else:
        print('There was an error')

    return anime_info

@app.route('/', methods=['GET', 'POST'])
def home():
    global anime_recommender
    if request.method == 'POST':
        search_term = request.form.get('search')
        user_name_list = str(search_term).split()
        print(user_name_list)
        try:
            recommendations = anime_recommender.recommend(user_name_list)
            session['recommendations'] = recommendations
            return redirect(url_for('rec_results'))
        except Exception as e:
            print(f'Exception in home: {e}')
    
    return render_template('index.html')

@app.route('/rec', methods=['GET', 'POST'])
def rec_results():
    global mongodb_client
    global anime_recommender

    if request.method == 'POST':
        search_term = request.form.get('search')
        print(search_term)
        user_name_list = str(search_term).split()
        print(user_name_list)
        try:
            recommendations = anime_recommender.recommend(user_name_list)
            session['recommendations'] = recommendations
            return redirect(url_for('rec_results'))
        except Exception as e:
            print(f'Exception in home: {e}')

    if 'recommendations' in session:
        recommendations = session['recommendations']
        rec_list = []
        for rec in recommendations:
            rec_dict = get_anime_info(int(float(rec)))
            rec_list.append(rec_dict)
        return render_template('rec.html', animes=rec_list)
    else:
        return redirect(url_for("home"))




if __name__ == '__main__':
    mongodb_client = setup_mongodb_client()
    anime_recommender = setup_anime_recommender()
    app.run(debug=True)