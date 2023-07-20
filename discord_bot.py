import discord
import traceback

def get_response(user_message : str, anime_recommender, mongodb_client):
    dbname = mongodb_client['MAL']
    anime_data = dbname['animelist']
    p_message = user_message.lower()
    embed_list = []

    if p_message[:4] == '!rec':
        user_name_list = str(p_message[5:]).split()
        try:
            recommendations = anime_recommender.recommend(user_name_list)
            print(f'length recommendations: {recommendations}')
        except Exception as e:
            print(f'Exception: {e}')
            print(traceback.format_exc())
            return (f"`There was a problem with your request.\n" 
        "Can you double check the spelling and make sure to write: '!rec <user_name>'?`"), embed_list
        
        if len(recommendations) > 0:
            bot_response = (f"# Hello *{', '.join(user_name_list)}* !\n## Here are my top anime "
                            "recommendations for you based on your favorite animes:\n")
            
            for i, anime_id in enumerate(recommendations):
                response = anime_data.find({"_id": anime_id})
                for element in response:
                    anime_dict = element

                genres = [genre['name'] for genre in anime_dict['genres']]
                genres = ', '.join(genres)

                anime_embed = discord.Embed(
                    title = f"**{i+1} - {anime_dict['title']}**",
                    url = f"https://myanimelist.net/anime/{anime_id}",
                    description = ("-----------------------------------------------------------------------   "
                                   f"\n> **Genres**: {genres}\n"
                                   f"> **Number of episodes**: {anime_dict['num_episodes']}\n"),
                     colour= discord.Color.teal())
                anime_embed.set_author(name = "MyAnimeRec",
                                       icon_url = ("https://e0.pxfuel.com/wallpapers"
                                            "/186/745/desktop-wallpaper-luffy-laughing-"
                                            "luffyriendo-onepiece-goldroger-smile.jpg"))
                anime_embed.set_thumbnail(url = anime_dict['main_picture']['medium'])

                embed_list.append(anime_embed)
        else:
            bot_response = (f"`I am sorry {', '.join(user_name_list)}, I wasn't able to find any" 
                            "animes to recommend for you. Please consider adding more ratings"
                            "to your MAL profile`")

        return bot_response, embed_list
    

async def send_messages(message, bot_response, embed_list, is_private):
    try:
        if is_private:
            await message.author.send(content = bot_response, embeds = embed_list)
        else:
            await message.channel.send(content = bot_response, embeds = embed_list)

    except Exception as e:
        print('here', e)
