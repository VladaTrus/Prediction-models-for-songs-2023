import pickle
import requests
import pandas as pd
import tqdm
import numpy as np
import time
import json

PT = 4
CLIENT_IDS = []
SECRETS = []
CREDENTIALS_POS = 0

artists_df_global = pd.read_csv("../../data/generated/1.1-spotify_artist_ids/artists_ids.csv")
artists_df_current = np.array_split(artists_df_global, 5)[PT-1]

with open("../../tokens/spotify_tokens.json", "r") as f:
    spotify_tokens_ = json.load(f)
    keys = [str(i+1) for i in range(5*(PT-1), 5*(PT-1)+5)]
    for key in keys:
        CLIENT_IDS.append(spotify_tokens_[key]['client_id'])
        SECRETS.append(spotify_tokens_[key]['secret'])


def refresh_token(push_credentials=False):
    global CREDENTIALS_POS, CLIENT_IDS, SECRETS
    # Step 1 - Authorization 
    import base64
    if push_credentials:
        CREDENTIALS_POS += 1
    client_id, client_secret = CLIENT_IDS[CREDENTIALS_POS], SECRETS[CREDENTIALS_POS]
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{client_id}:{client_secret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')


    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "client_credentials"

    r = requests.post(url, headers=headers, data=data)
    token_ = r.json()['access_token']
    return token_

HEADERS = {"Authorization": "Bearer " + refresh_token()}

def send_request(URL):
    n_tries = 0

    global HEADERS

    while True:
        if n_tries > 3:
            HEADERS = {"Authorization": "Bearer " + refresh_token(push_credentials=True)}
            n_tries = 0
        try:
            res = requests.get(url=URL, headers=HEADERS).json()
            return res
        except Exception:
            n_tries += 1
            print("Unable to send GET, sleeping for 50 seconds...")
            time.sleep(5)


artists_df_current[['followers', 'genres', 'image_url', 'popularity']] = pd.NA
df_size = artists_df_current.shape[0]

rows = []
for i, row in tqdm.tqdm(artists_df_current.copy().iterrows(), total=df_size):
    artist_id = row['artist_id']
    URL = f"https://api.spotify.com/v1/artists/{artist_id}"
    resp = send_request(URL)
    
    if "error" in resp and resp['error']['message'] in {"Invalid access token", "The access token expired"}:
            resp = send_request(URL)
    elif "error" in resp:
        continue
    else:
        followers = resp['followers']['total']
        genres = '||'.join(resp['genres'])
        image_urls = resp['images']
        if image_urls:
            image_urls.sort(key=lambda x: x['height'], reverse=True)
            image_url = image_urls[0]['url']
        else:
            image_url = ""
        popularity = resp['popularity']

        row[['followers', 'genres', 'image_url', 'popularity']] = [followers, genres, image_url, popularity]
        rows.append(row)
    if i % 500 == 0 and i != 0:
        sub_df = pd.DataFrame(rows)
        with open(f"extracted_artists_info/pt_{PT}/artists_info_{i-500}_{i}.pickle", "wb") as f:
            pickle.dump(sub_df, f)
        rows = []
if rows:
    sub_df = pd.DataFrame(rows)
    with open(f"extracted_artists_info/pt_{PT}/artists_info_{df_size - (df_size % 500)}_{df_size}.pickle", "wb") as f:
        pickle.dump(sub_df, f)
