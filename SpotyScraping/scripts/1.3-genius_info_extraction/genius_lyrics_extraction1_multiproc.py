from os import listdir, walk
import pickle
import pandas as pd
from tqdm import tqdm
import numpy as np
import json
import lyricsgenius
from genius_funcs import *
from threading import Thread
import queue
from threading import Lock


class MusicThreader(Thread):

    GEN_APIS = []
    APIS_LOCK = Lock()
    def create_api_list(tokens):
        MusicThreader.GEN_APIS = tokens

    def pull_token():
        while True:
            if MusicThreader.GEN_APIS:
                return MusicThreader.GEN_APIS.pop()
            else:
                time.sleep(3)
    def push_token(token):
        MusicThreader.GEN_APIS.append(token)

    def __init__(self, artist_name, music_obj_name, music_obj_type, gen_api):
        super().__init__()
        self.artist_name = artist_name
        self.music_obj_name = music_obj_name
        self.music_obj_type = music_obj_type
        self.gen_api = gen_api  
    
    

    def run(self):
        gen_api = MusicThreader.pull_token()

        if self.music_obj_type == 'album':
            self.album_data = collect_album_data(self.artist_name, self.music_obj_name, gen_api)    
        else:
            self.single_data = collect_single_data(self.artist_name, self.music_obj_name, gen_api)   

        MusicThreader.push_token(gen_api)

def process_artist(sub_df, artist_id):
    
    artist_discography = {artist_id: []}
    artist_name = sub_df['artist_name'].iloc[0]
    data_saved = []
    saved_full = False

    tracks_collected = 0
    tracks_traversed = 0


    tracks_max = sub_df['n_tracks'].sum()

    music_threads = []
    for i, df_row in sub_df.iterrows():
        album_id = df_row['album_id']
        album_name = df_row['album_name']
        album_type = df_row['album_type']
        music_thread = MusicThreader(artist_name, album_name, album_type)
        music_threads.append(music_thread)
    
    

    


PT = '1'
LEFT_SUFFIX = ''
EXTRACTION_PATH = "../../data/generated/1.3-genius_ids_to_load"

if f"artists_ids_pt{PT}_left.pickle" in listdir(EXTRACTION_PATH):
    LEFT_SUFFIX = '_left'


with open("../../tokens/genius_tokens.json", "r") as f:
    genius_tokens = json.load(f)
    genius_access_token = genius_tokens[PT]['access_token']


with open(f"{EXTRACTION_PATH}/artists_ids_pt{PT}{LEFT_SUFFIX}.pickle", "rb") as f1, \
    open(f"{EXTRACTION_PATH}/artists_and_albums_ids_pt{PT}.pickle", "rb") as f2:
    artists_ids = pickle.load(f1)
    df_artists_albums = pickle.load(f2)

gen_api = lyricsgenius.Genius(genius_access_token, verbose=False, retries=5)

artists_ids_left = artists_ids.copy()

for artist_id in tqdm(artists_ids):

    sub_df = df_artists_albums[df_artists_albums['artist_id'] == artist_id]
    sub_df = sub_df.sort_values(by='release_date', ascending=False)

    artist_discography = process_artist(artist_id, sub_df)

    for i, df_row in sub_df.iterrows():
        album_id = df_row['album_id']
        album_name = df_row['album_name']
        album_type = df_row['album_type']
        tracks_traversed += df_row['n_tracks']
        
        if album_type == 'album':
            album_data = collect_album_data(artist_name, album_name, gen_api)
            if not album_data:
                continue
            album_info, n_tracks = process_album_data(album_data, album_id, album_name, album_type)
            
            
        elif album_type == 'single':
            single_data = collect_single_data(artist_name, album_name, gen_api)
            if not single_data:
                continue
            album_info = [process_track_data(single_data, is_single=True) + [album_id, album_name, album_type]]
            n_tracks = 1

        
        tracks_collected  += n_tracks

        artist_discography[artist_id].append([album_info, n_tracks])
        if tracks_max - tracks_traversed + tracks_collected < 15:
            with open(f"genius_track_info_extracted/artists_not_enough_data/{artist_id}.pickle", "wb") as f:
                pickle.dump(artist_discography, f)
            break
        
        if tracks_collected > 65:
            with open(f"genius_track_info_extracted/genius_artists_pt{PT}/{artist_id}.pickle", "wb") as f:
                pickle.dump(artist_discography, f)
            saved_full = True
            break
    
    if not saved_full:
        with open(f"genius_track_info_extracted/artists_not_enough_data/{artist_id}.pickle", "wb") as f:
            pickle.dump(artist_discography, f)

    artists_ids_left = np.delete(artists_ids_left, 0)
    
    
    with open(f"{EXTRACTION_PATH}/artists_ids_pt{PT}_left.pickle", "wb") as f1:
        pickle.dump(artists_ids_left, f1)
