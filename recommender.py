import requests
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class Recommender():

    def __init__(self, synopsis_sim, genres_sim, token, client, df_animelist) -> None:
        self.synopsis_sim = synopsis_sim
        self.genres_sim = genres_sim
        self.token = token
        self.client = client
        self.df_animelist = df_animelist
        self.indices = pd.Series(self.df_animelist.index, index=self.df_animelist['id']).drop_duplicates()

    def get_user_data(self, user_name):
        data_list = []
        user_dict = {}
        url = f"https://api.myanimelist.net/v2/users/{user_name}/animelist?offset=0&sort=list_score&limit=100&fields=list_status'"

        try:
            i = 0
            done = False
            while not done:
                print(f'\nStarting loop {i}')
                i += 1
                response = requests.get(url, headers = {
                        'Authorization': f"Bearer {self.token['access_token']}"
                        })
                response.raise_for_status()
                user_list = response.json()
                response.close()
                for anime in user_list['data']:
                    anime_dict = dict(anime['node'])
                    anime_dict.update(anime['list_status'])
                    data_list.append(anime_dict)
                if 'next' in user_list['paging']:
                    url = user_list['paging']['next']
                    print(f'Next: {url}')
                else:
                    done = True
                    print('This is the last iteration')
        except Exception as e:
            print(f'\nException: {e}')

        user_dict['_id'] = user_name
        user_dict['data'] = data_list
        
        #check if user id exists or not to know if update or insert
        dbname = self.client['MAL']
        user_data = dbname['userdata']
        if not user_dict['data']:
            pass
        elif user_data.count_documents({'_id':user_name}) > 0:
            user_data.replace_one({'_id':user_name}, user_dict)
        else:
            user_data.insert_one(user_dict)

        return user_dict
    
    def userlist_to_dataframe(self, user_dict):
        anime_id_list = []
        score_list = []

        for anime in user_dict['data']:
            id = anime['id']
            score = anime['score']
            anime_id_list.append(id)
            score_list.append(score)
        user_df = pd.DataFrame({'anime_id': anime_id_list, 'score': score_list})

        return user_df

    def get_user_favorite(self, user_df):
        threshold = 8
        aux = user_df.loc[user_df['score'] >= threshold]
        favorite_list = list(aux['anime_id'].values)

        return favorite_list
    
    def find_similar_animes(self, favorite_list):
        similar_animes = {}

        for anime in favorite_list:
            try:
                idx = self.indices[anime]
                synopsis_sim_scores = list(self.synopsis_sim[idx])
                genres_sim_scores =  list(self.genres_sim[idx])
                anime_df = pd.DataFrame({'synopsis_similarity': synopsis_sim_scores, 'genres_similarity': genres_sim_scores})
                similar_animes[anime] = anime_df
            except Exception as e:
                print(e)

        return similar_animes
    
    def filter_low_ratings(self, similar_animes):
        threshold = 7
        for anime in similar_animes:
            anime_df = similar_animes[anime]
            merged_df = pd.merge(anime_df, self.df_animelist['rating'], left_index=True, right_index=True)
            merged_df = merged_df[merged_df.rating >= threshold]
            similar_animes[anime] = merged_df

        return similar_animes
    
    def filter_already_inlist(self, similar_animes, user_name):
        dbname = self.client['MAL']
        user_data = dbname['userdata']
        response = user_data.find({'_id': user_name})
        user_dict = next(response, None)

        already_inlist = []
        for anime in user_dict['data']:
            already_inlist.append(anime['id'])
        
        local_animelist = self.df_animelist[self.df_animelist['id'].isin(already_inlist)]
        already_inlist_index = local_animelist.index.tolist()
        
        filtered_animes = {}
        for anime in similar_animes:
            anime_df = similar_animes[anime]
            filtered_df = anime_df.drop(anime_df.index[anime_df.index.isin(already_inlist_index)])
            filtered_animes[anime] = filtered_df

        return filtered_animes
    
    def merge_anime_df(self, filtered_animes):
        merged_df = pd.DataFrame()

        for anime in filtered_animes:
            anime_df = filtered_animes[anime]
            merged_df = pd.concat([merged_df, anime_df])

        return merged_df
    
    def rank_anime(self, merged_df):
        scaler = MinMaxScaler()
        merged_df['scaled_synopsis_similarity'] = scaler.fit_transform(merged_df[['synopsis_similarity']])
        merged_df['scaled_genres_similarity'] = scaler.fit_transform(merged_df[['genres_similarity']])
        merged_df['scaled_rating'] = scaler.fit_transform(merged_df[['rating']])
        #Taking the average of the scaled similarity and score to establish final rank
        merged_df['ranking'] = (0.6 * merged_df['scaled_genres_similarity']) + (0.15 * merged_df['scaled_rating']) + (0.25 * merged_df['scaled_synopsis_similarity'])
        merged_df = merged_df.sort_values(by='ranking', ascending=False)
        merged_df = merged_df[~merged_df.index.duplicated(keep='first')]
        
        ranking_df = merged_df['ranking'].to_frame()

        return ranking_df
    
    def select_top_10(self, ranking_df_list):
        final_df = pd.concat(ranking_df_list, axis=1, join='inner')
        final_df['average'] = final_df.mean(axis=1)

        top_animes = final_df.nlargest(10, 'average').index.tolist()
        #Transforming the index values into anime_id values.
        top_animes_id = []
        for index in top_animes:
            anime_id = self.df_animelist.loc[index]['id']
            top_animes_id.append(int(anime_id))

        return top_animes_id

    def recommend(self, user_name_list):
        #First user recommendations
        ranking_df_list = []
        for user_name in user_name_list:
            user_dict = self.get_user_data(user_name)
            user_df = self.userlist_to_dataframe(user_dict)
            favorite_list = self.get_user_favorite(user_df)
            similar_animes = self.find_similar_animes(favorite_list)
            similar_animes = self.filter_low_ratings(similar_animes)
            filtered_animes = self.filter_already_inlist(similar_animes, user_name)
            merged_df = self.merge_anime_df(filtered_animes)
            ranking_df = self.rank_anime(merged_df)
            ranking_df_list.append(ranking_df)
        
        top_animes_id = self.select_top_10(ranking_df_list)
        print(f'Top ANIMES: {top_animes_id}')

        dbname = self.client['MAL']
        rec_data = dbname['recommendation']
        
        for user_name in user_name_list:
            if rec_data.count_documents({'_id': user_name}) > 0:
                response = rec_data.find({'_id': user_name})
                user_rec = next(response, None)
                recommendations = list(set(top_animes_id + user_rec['recommendations'])) 
                rec_data.replace_one({'_id': user_name}, {'_id': user_name, 'recommendations': recommendations})
            else:
                rec_dict = {'_id': user_name, 
                            'recommendations': top_animes_id}
                rec_data.insert_one(rec_dict)
            
        return top_animes_id