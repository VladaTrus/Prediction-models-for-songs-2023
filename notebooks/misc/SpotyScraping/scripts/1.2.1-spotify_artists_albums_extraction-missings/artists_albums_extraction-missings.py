import json
import pickle
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import tqdm

CLIENT_IDS = []
SECRETS = []
CREDENTIALS_POS = 0
SAVE_CHUNK_SIZE = 500

albums_df_missings = pd.read_csv("to_extract.csv")
# if no more missings left
if not albums_df_missings.shape[0]:
    exit()

with open("../../tokens/spotify_tokens.json", "r") as f:
    spotify_tokens_ = json.load(f)
    keys = [str(i + 1) for i in range(20)]
    for key in keys:
        CLIENT_IDS.append(spotify_tokens_[key]["client_id"])
        SECRETS.append(spotify_tokens_[key]["secret"])


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
    messageBytes = message.encode("ascii")
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode("ascii")

    headers["Authorization"] = f"Basic {base64Message}"
    data["grant_type"] = "client_credentials"

    r = requests.post(url, headers=headers, data=data)
    token_ = r.json()["access_token"]
    return token_


HEADERS = {"Authorization": "Bearer " + refresh_token()}


def send_request(URL):
    n_tries = 0

    global HEADERS

    while True:
        if n_tries > 3:
            HEADERS = {
                "Authorization": "Bearer " + refresh_token(push_credentials=True)
            }
            n_tries = 0
        try:
            res = requests.get(url=URL, headers=HEADERS).json()
            return res
        except Exception:
            n_tries += 1
            print("Unable to send GET, sleeping for 5 seconds...")
            time.sleep(5)


df_size = albums_df_missings.shape[0]

rows = []
ids_found = []
for i, row in tqdm.tqdm(albums_df_missings.copy().iterrows(), total=df_size):
    artist_id = row["artist_id"]
    URL = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups=album,single"
    resp = send_request(URL)
    if "error" in resp and resp["error"]["message"] in {
        "Invalid access token",
        "The access token expired",
    }:
        resp = send_request(URL)
    elif "error" in resp:
        pass
    else:
        for item_ in resp["items"]:
            album_type = item_["album_type"]
            artists = "|".join(
                [i["id"] for i in item_["artists"] if i["type"] == "artist"]
            )
            album_id = item_["id"]
            album_name = item_["name"]
            release_date = item_["release_date"]
            n_tracks = item_["total_tracks"]

            rows.append(
                [
                    artist_id,
                    album_id,
                    album_name,
                    album_type,
                    artists,
                    release_date,
                    n_tracks,
                ]
            )
        ids_found.append(artist_id)

    if i % SAVE_CHUNK_SIZE == 0 and i != 0:
        sub_df = pd.DataFrame(
            rows,
            columns=[
                "artist_id",
                "album_id",
                "album_name",
                "album_type",
                "artists",
                "release_date",
                "n_tracks",
            ],
        )
        timestamp_ = str(datetime.now().timestamp()).replace(".", "_")
        with open(
            f"../1.2-spotify_artists_albums_extraction/extracted_albums_info/missings/missings_{timestamp_}.pickle",
            "wb",
        ) as f:
            pickle.dump(sub_df, f)
        rows = []
        new_missings = albums_df_missings[
            ~albums_df_missings["artist_id"].isin(set(ids_found))
        ]
        new_missings.to_csv("to_extract.csv", index=False)
if rows:
    sub_df = pd.DataFrame(
        rows,
        columns=[
            "artist_id",
            "album_id",
            "album_name",
            "album_type",
            "artists",
            "release_date",
            "n_tracks",
        ],
    )
    timestamp_ = str(datetime.now().timestamp()).replace(".", "_")
    with open(
        f"../1.2-spotify_artists_albums_extraction/extracted_albums_info/missings/missings_{timestamp_}.pickle",
        "wb",
    ) as f:
        pickle.dump(sub_df, f)


new_missings = albums_df_missings[~albums_df_missings["artist_id"].isin(set(ids_found))]
new_missings.to_csv("to_extract.csv", index=False)
