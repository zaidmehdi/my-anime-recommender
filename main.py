from recommender import Recommender
import discord
from discord_bot import get_response, send_messages
import json
from pymongo import MongoClient
import joblib
import pandas as pd



if __name__ == '__main__':
    with open('discord_token.txt', 'r') as f:
        discord_token = f.read()

    f = open('mal_token.json')
    mal_token = json.load(f)

    with open('mongodb_server.txt', 'r') as f:
        CONNECTION_STRING = f.read()
    
    mongodb_client = MongoClient(CONNECTION_STRING)

    df_animelist = pd.read_csv('df_animelist.csv')
    synopsis_sim = joblib.load('synopsis_sim.pkl')

    anime_recommender = Recommender(synopsis_sim, mal_token, mongodb_client, df_animelist)

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            pass
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})') 

        if user_message[0] == 'p':
            user_message = user_message[1:]
            bot_response = get_response(user_message, anime_recommender, mongodb_client)
            await send_messages(message, bot_response, is_private=True)
        else:
            bot_response = get_response(user_message, anime_recommender, mongodb_client)
            await send_messages(message, bot_response, False)

    client.run(discord_token)