import json
import os
import re
import time

import lyricsgenius
import pandas as pd
from decouple import config

ACCESS_TOKEN = config('ACCESS_TOKEN')
PATH_TO_DATA = '../SoundOfDownloader/'


class LyricsScraper:
    def __init__(self, access_token):
        self.genius = lyricsgenius.Genius(access_token)
        self.found_lyrics_dict = {}
        self.not_found_tracks = set()
        self.counter = 0


    def get_lyrics_and_save(self, row, found_lyrics_filename='raw_lyrics.json', not_found_tracks_filename='not_found_tracks.json'):
        """
        Get lyrics for a song using various search options and simultaneously save to pickles.

        Parameters:
        - row: DataFrame row containing relevant information (e.g., 'track_name', 'track_artists_names', 'track_id')
        - found_lyrics_filename: Filename for the pickle containing found lyrics
        - not_found_tracks_filename: Filename for the pickle containing not found tracks

        Returns:
        - Lyrics for the specified song
        """
        song_title = row['track_name']
        artist_name = row['track_artists_names']
        track_id = row['track_id']

        try:
            found_song = self._fetch_song_object(song_title, artist_name)
            lyrics, artist, title = found_song.lyrics, found_song.artist, found_song.title
            if lyrics and self._is_valid_match(found_song, song_title, artist_name):
                print('sucess')
                # Store the lyrics in the dictionary along with track_id
                self.found_lyrics_dict[track_id] = lyrics
                self.save_to_json(found_lyrics_filename, self.found_lyrics_dict)
                self.counter += 1
                if self.counter % 10 == 0:
                    print(f"Processed {self.counter} songs")
                return lyrics
            else:
                # If lyrics are not found or not a valid match, add the track_id to the set of not_found_tracks
                print('fail')
                self.not_found_tracks.add(track_id)
                self.save_to_json(not_found_tracks_filename, self.not_found_tracks)
                return f"Lyrics for {song_title} by {artist_name} not found or not a valid match."
        except Exception as e:
            print(f"An error occurred while processing {song_title} by {artist_name}: {e}")
            return None

    def _fetch_song_object(self, song_title, artist_name, max_retries=3):
        """
        Fetch lyrics based on the specified search option.

        Parameters:
        - song_title: Title of the song
        - artist_name: Name of the artist

        Returns:
        - Lyrics if found, else None
        """
        for _ in range(max_retries):
            try:
                # Split the artists in case there are multiple
                artists = artist_name.split(':artist_custom_separator:')
                for artist in artists:
                    artist = artist.strip()
                    print(artist)
                    song = self.genius.search_song(song_title, artist)
                    if song:
                        return song
            except Exception as e:
                raise e

        return None

    def _is_valid_match(self, song, target_title, target_artist):
        """
        Check if the returned song is a valid match for the specified title and artist.

        Parameters:
        - song: Genius API song object
        - target_title: Title of the target song
        - target_artist: Name of the target artist

        Returns:
        - True if the song is a valid match, else False
        """
        return (
            target_title.lower() in song.title.lower() and
            any(target_artist.lower() in artist.name.lower() for artist in song.song_artists)
        )

    def save_to_json(self, filename, data):
        """Save data to a JSON file."""
        with open(filename, 'w') as json_file:
            json.dump(data, json_file)

    def load_from_json(self, filename):
        """Load data from a JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                return json.load(json_file)
    

def remove_patterns(song_name):
    patterns_to_remove = [
        r'\s*-\s*[\w\'\(\)\[\]]*\s*(?:[vV]ersion|[rR]emix|[rR]emaster|[aA]coustic|[sS]ingle|RMX|[rR]emastered|B-side|[rR]adio|[eE]dit|Live|[uU]nplugged|[dD]emo|Bonus|Idol|Season|Session|[sS]tripped|[mM]ix|[sS]tudio)\s*\w*',
        r'\s*\[[^\]]*(?:[Ff]eat\.|ft\.)[^\]]*\]\s*',
        r'\s*-\s*Remix\s*.*',
        r'\s*-\s*\d{4}\s*',
        r'\s*From\s*".*?"\s*[sS}oundtrack|[mM]otion [Pp]icture|[sS]eries\s*',
        'Spider-Man: Into the Spider-Verse',
        r'/\s*\w*\s*Version',
        r'\s*Theme from\s*".*?"\s*',
        r'\s*\[[^\]]*(?:[Ff]eat\.|[Ff]t\.)[^\]]*\]\s*',
        r'\(feat\.[^\)]*\)',
        r'\(from\s*".*?"\)', 
        r'\(Live|Acoustic|Remix\)',
        r'\(\*\w+\s*Remaster\)',
    ]

    for pattern in patterns_to_remove:
        song_name = re.sub(pattern, '', song_name)

    # Remove extra whitespaces
    song_name = re.sub(r'\s+', ' ', song_name).strip()

    return song_name

if __name__ == "__main__":
    lyrics_scraper = LyricsScraper(ACCESS_TOKEN)
    tracks_df = pd.read_pickle(f'{PATH_TO_DATA}tracks_df.pickle')
    tracks_df['track_name'] = tracks_df['track_name'].apply(remove_patterns)

    for index, row in tracks_df.iterrows():
        try:
            lyrics = lyrics_scraper.get_lyrics_and_save(row)
            print(index, lyrics)
        except Exception as e:
            print(f"An error occurred: {e}")    
