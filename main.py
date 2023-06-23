import json
import discord
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from recommender import Recommender
from discord_bot import get_response, send_messages
from anime_similarity import create_df_animelist, calculate_cosine_similarity


if __name__ == '__main__':
    with open('tokens/discord_token.txt', 'r') as f:
        discord_token = f.read()

    f = open('tokens/mal_token.json')
    mal_token = json.load(f)

    with open('tokens/mongodb_server.txt', 'r') as f:
        url = f.read()
    
    mongodb_client = MongoClient(url, server_api=ServerApi('1'))

    df_animelist = create_df_animelist(mongodb_client)
    synopsis_sim = calculate_cosine_similarity(df_animelist, 'synopsis')
    genres_sim = calculate_cosine_similarity(df_animelist, 'genres')

    anime_recommender = Recommender(synopsis_sim, genres_sim, mal_token, mongodb_client, df_animelist)

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        try:
            if message.author == client.user:
                pass
            
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f'{username} said: "{user_message}" ({channel})') 

            if user_message[0] == 'p':
                user_message = user_message[1:]
                bot_response, embed_list = get_response(user_message, anime_recommender, mongodb_client)
                await send_messages(message, bot_response, embed_list, is_private=True)
            else:
                bot_response, embed_list = get_response(user_message, anime_recommender, mongodb_client)
                await send_messages(message, bot_response, embed_list, False)
        except TypeError as e:
            print(e)

    client.run(discord_token)