import time

def is_track_ok(track):
    song_dict = track.__dict__['song'].__dict__
    if song_dict['lyrics_state'] != 'complete':
        return False
    if song_dict['_body']['instrumental']:
        return False
    if song_dict['_body']['language'] != "en":
        return False
    if not song_dict['lyrics']:
        return False
    
    return True

def process_track_data(track, is_single=False):

    if is_single:
        song_dict = track.__dict__
    else:
        song_dict = track.__dict__['song'].__dict__

    # track data
    lyrics = song_dict['lyrics']
    annotation_count = song_dict['_body']['annotation_count']
    title_ = song_dict['_body']['title']
    title_with_featured = song_dict['_body']['title_with_featured']
    track_id = song_dict['_body']['id']
    
    _stats = song_dict['_body']['stats']
    try:
        is_hot = _stats['hot']
    except KeyError:
        is_hot = None

    try:
        pageviews = _stats['pageviews']
    except KeyError:
        pageviews = None
    
    # artist data
    
    primary_artist_raw = song_dict['_body']['primary_artist']
    primary_artist_id = primary_artist_raw['id']
    primary_artist_name = primary_artist_raw['name']
    
    featured_artists_raw = song_dict['_body']['featured_artists']
    if featured_artists_raw:
        featured_artists = [[i['_type'], i['id'], i['name']] for i in featured_artists_raw]
    else:
        featured_artists = []
    
    return [[track_id, title_, title_with_featured, annotation_count, is_hot, pageviews, lyrics, 
            primary_artist_id, primary_artist_name], featured_artists]

def collect_album_data(artist_name, album_name, gen_api):
    attempts = 0
    while True:
        try:
            if attempts > 2:
                print(f"Album search failed, trying {attempts} time")
            if "'" in album_name:
                album_name = album_name.replace("'", "`")
            album_data = gen_api.search_album(name=album_name, artist=artist_name)
            return album_data
        except Exception:  # timeout error
            time.sleep(3)
            attempts += 1
    
def process_album_data(album_, *args):
    album_tracks = album_.__dict__['tracks']
    n_tracks_album = len(album_.__dict__['tracks'])
    album_data = []
    for track in album_tracks:
        if not is_track_ok(track):
            
            continue

        track_info_genius, featured_artists = process_track_data(track)
        album_data.append([track_info_genius, featured_artists, args]) # album_id_spotify, album_name_spotify, album_type_spotify, 
    return album_data, n_tracks_album

def collect_single_data(artist_name, single_name, gen_api):
    attempts = 0
    while True:
        try:
            if attempts > 2:
                print(f"Single search failed, trying {attempts} time")
            if "'" in single_name:
                single_name = single_name.replace("'", "`")
            single_data = gen_api.search_song(title=single_name, artist=artist_name)
            return single_data
        except Exception:  # timeout error
            time.sleep(3)
            attempts += 1
