import discord

def get_response(user_message : str, anime_recommender, mongodb_client):
    dbname = mongodb_client['MAL']
    anime_data = dbname['animelist']
    p_message = user_message.lower()

    if p_message[:4] == '!rec':
        user_name = p_message[5:]
        try:
            recommendations = anime_recommender.recommend(user_name)
        except Exception:
            return (f"`I didn't find any user called '{user_name}' on MAL.\n" 
        "Can you double check the spelling and make sure to write: '!rec <user_name>'?`")
        
        if len(recommendations) > 0:
            bot_response = (f"# Hello *{user_name}* !\n## Here are my top anime "
                            "recommendations for you based on your favorite animes:\n")
            
            embed_list = []
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
                                       icon_url = ("https://yt3.googleusercontent.com/"
                                       "Ntsi7XsgokCIX3ljFAk40ll1Nesi3QqCDFwPTjVlg"
                                       "lZuS0qocpOOH0vE0jtKCMBJTuO-gBbQ5A=s900-c-k-c0x00ffffff-no-rj"))
                anime_embed.set_thumbnail(url = anime_dict['main_picture']['medium'])

                embed_list.append(anime_embed)

                # bot_response += (f"\n> {mal_link}\n"
                #                  f"> **Genres**: {genres}\n"
                #                  f"> **Number of episodes**: {anime_dict['num_episodes']}\n")
                
        else:
            bot_response = (f"`I am sorry {user_name}, I wasn't able to find any" 
                            "animes to recommend for you. Please consider adding more ratings"
                            "to your MAL profile`")

        return bot_response, embed_list
    
    if p_message == '!test':
        return 'Your test is working'

async def send_messages(message, bot_response, embed_list, is_private):
    try:
        if is_private:
            await message.author.send(content = bot_response, embeds = embed_list)
        else:
            await message.channel.send(content = bot_response, embeds = embed_list)

    except Exception as e:
        print('here', e)
