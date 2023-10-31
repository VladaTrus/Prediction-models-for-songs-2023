import pickle
import requests
import pandas as pd
import tqdm
import numpy as np
import time
import json
from datetime import datetime

CLIENT_IDS = []
SECRETS = []
CREDENTIALS_POS = 0

artists_df_missings = pd.read_csv("to_extract.csv")
# if no more missings left
if not artists_df_missings.shape[0]:
    exit()

with open("../../tokens/spotify_tokens.json", "r") as f:
    spotify_tokens_ = json.load(f)
    keys = [str(i+1) for i in range(20)]
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
            print("Unable to send GET, sleeping for 5 seconds...")
            time.sleep(5)


artists_df_missings[['followers', 'genres', 'image_url', 'popularity']] = pd.NA
df_size = artists_df_missings.shape[0]

rows = []
ids_found = []
for i, row in tqdm.tqdm(artists_df_missings.copy().iterrows(), total=df_size):
    artist_id = row['artist_id']
    URL = f"https://api.spotify.com/v1/artists/{artist_id}"
    resp = send_request(URL)
    
    if "error" in resp and resp['error']['message'] in {"Invalid access token", "The access token expired"}:
            resp = send_request(URL)
    elif "error" in resp:
        pass
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
        ids_found.append(artist_id)
    if i % 500 == 0 and i != 0 and rows:
        sub_df = pd.DataFrame(rows)
        timestamp_ = str(datetime.now().timestamp()).replace(".", "_")
        with open(f"../1.1-spotify_artists_info_extraction/extracted_artists_info/missings/missings_{timestamp_}.pickle", "wb") as f:
            pickle.dump(sub_df, f)
        rows = []
        

if rows:
    sub_df = pd.DataFrame(rows)
    timestamp_ = str(datetime.now().timestamp()).replace(".", "_")
    with open(f"../1.1-spotify_artists_info_extraction/extracted_artists_info/missings/missings_{timestamp_}.pickle", "wb") as f:
        pickle.dump(sub_df, f)

new_missings = artists_df_missings[~artists_df_missings['artist_id'].isin(set(ids_found))]
new_missings.to_csv("to_extract.csv", index=False)