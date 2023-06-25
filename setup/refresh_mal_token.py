import requests
import json

CLIENT_ID = 'ddd3d9dc84435041d4ff00093cc116f3'
CLIENT_SECRET = '3d7722cd1756b0dac80d4fcfa049cad1b12fd42fb1961dd44fbb928cd8523727'


def refresh_token(refresh_token: str):
    global CLIENT_ID, CLIENT_SECRET

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the request contains errors

    token = response.json()
    response.close()
    print('Token generated successfully!')

    with open('tokens/mal_token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "tokens/mal_token.json"')

    return token


if __name__ == '__main__':
    with open('tokens/mal_token.json') as file:
        old_token = json.load(file)

    new_token = refresh_token(old_token['refresh_token'])
