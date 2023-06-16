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
            bot_response = (f"`Hello there, {user_name}!\nHere are my top anime "
                            "recommendations for you based on your favorite animes:\n")
            
            for i, anime_id in enumerate(recommendations):
                response = anime_data.find({"_id": anime_id})
                for element in response:
                    anime_dict = element

                genres = [genre['name'] for genre in anime_dict['genres']]
                bot_response += (f"\n{i+1} - {anime_dict['title']}\n"
                                 f"Genres: {genres}\n"
                                 f"Number of episodes: {anime_dict['num_episodes']}\n")

            bot_response += "`"
        else:
            bot_response = (f"`I am sorry {user_name}, I wasn't able to find any" 
                            "animes to recommend for you. Please consider adding more ratings"
                            "to your MAL profile`")

        return bot_response
    
    if p_message == '!test':
        return 'Your test is working'

async def send_messages(message, bot_response, is_private):
    try:
        if is_private:
            await message.author.send(bot_response)
        else:
            await message.channel.send(bot_response)

    except Exception as e:
        print(e)
