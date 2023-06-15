
def get_response(message, anime_recommender):
    p_message = message.lower()

    if p_message[:3] == 'rec':
        user_name = p_message[4:]
        recommendations = anime_recommender.recommend(user_name)

        return f'Your recommendations: {recommendations}'

    if p_message == 'test':
        return 'Your test is working'

async def send_messages(message, bot_response, is_private):
    try:
        if is_private:
            await message.author.send(bot_response)
        else:
            await message.channel.send(bot_response)

    except Exception as e:
        print(e)
