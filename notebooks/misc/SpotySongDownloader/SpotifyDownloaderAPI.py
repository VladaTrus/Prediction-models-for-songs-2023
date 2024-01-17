import csv
import json
import os
import urllib
from os import path
from pathlib import Path, PurePath

import mutagen
import spotipy
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from rich.progress import Progress
from spotipy import SpotifyClientCredentials

with open("configs/constants.json", "r") as f:
    constants = json.load(f)
    OUTPUT_DIR = constants["OUTPUT_DIR"]
    DOWNLOAD_LIST = constants["DOWNLOAD_LIST"]

with open("configs/spotify_config.json", "r") as f:
    SPOTIFY_CONFIG = json.load(f)
client_id = SPOTIFY_CONFIG["client_id"]
client_secret = SPOTIFY_CONFIG["client_secret"]

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
)


def parse_spotify_url(url):
    """
    Parse the provided Spotify playlist URL and determine if it is a playlist, track or album.
    :param url: URL to be parsed

    :return tuple indicating the type and id of the item
    """
    if url.startswith("spotify:"):
        log.error("Spotify URI was provided instead of a playlist/album/track URL.")
        sys.exit(1)
    parsed_url = url.replace("https://open.spotify.com/", "").split("?")[0].split("/")
    index_adjustment = 1 if parsed_url[0].startswith("intl") else 0
    item_type = parsed_url[0 + index_adjustment]
    item_id = parsed_url[1 + index_adjustment]
    return item_type, item_id


def sanitize(name, replace_with=""):
    """
    Removes some of the reserved characters from the name so it can be saved
    :param name: Name to be cleaned up
    :return string containing the cleaned name
    """
    clean_up_list = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "\0", "$", '"']
    for x in clean_up_list:
        name = name.replace(x, replace_with)
    return name


def get_item_name(sp, item_type, item_id):
    """
    Fetch the name of the item.
    :param sp: Spotify Client
    :param item_type: Type of the item
    :param item_id: id of the item
    :return String indicating the name of the item
    """
    if item_type == "playlist":
        name = sp.playlist(playlist_id=item_id, fields="name").get("name")
    elif item_type == "album":
        name = sp.album(album_id=item_id).get("name")
    elif item_type == "track":
        name = sp.track(track_id=item_id).get("name")
    return sanitize(name)


def fetch_tracks(sp, item_type, item_id):
    """
    Fetches tracks from the provided item_id.
    :param sp: Spotify client
    :param item_type: Type of item being requested for: album/playlist/track
    :param item_id: id of the item
    :return Dictionary of song and artist
    """
    songs_list = []
    offset = 0
    songs_fetched = 0

    if item_type == "playlist":
        with Progress() as progress:
            songs_task = progress.add_task(description="Fetching songs from playlist..")
            while True:
                items = sp.playlist_items(
                    playlist_id=item_id,
                    fields="items.track.name,items.track.artists(name, uri),"
                    "items.track.album(name, release_date, total_tracks, images),"
                    "items.track.track_number,total, next,offset,"
                    "items.track.id",
                    additional_types=["track"],
                    offset=offset,
                )
                total_songs = items.get("total")
                track_info_task = progress.add_task(
                    description="Fetching track info", total=len(items["items"])
                )
                for item in items["items"]:
                    track_info = item.get("track")
                    # If the user has a podcast in their playlist, there will be no track
                    # Without this conditional, the program will fail later on when the metadata is fetched
                    if track_info is None:
                        offset += 1
                        continue
                    track_album_info = track_info.get("album")
                    track_num = track_info.get("track_number")
                    spotify_id = track_info.get("id")
                    track_name = track_info.get("name")
                    track_artist = ", ".join(
                        [artist["name"] for artist in track_info.get("artists")]
                    )
                    if track_album_info:
                        track_album = track_album_info.get("name")
                        track_year = (
                            track_album_info.get("release_date")[:4]
                            if track_album_info.get("release_date")
                            else ""
                        )
                        album_total = track_album_info.get("total_tracks")
                    if len(item["track"]["album"]["images"]) > 0:
                        cover = item["track"]["album"]["images"][0]["url"]
                    else:
                        cover = None

                    artists = track_info.get("artists")
                    main_artist_id = (
                        artists[0].get("uri", None) if len(artists) > 0 else None
                    )
                    genres = (
                        sp.artist(artist_id=main_artist_id).get("genres", [])
                        if main_artist_id
                        else []
                    )
                    if len(genres) > 0:
                        genre = genres[0]
                    else:
                        genre = ""
                    songs_list.append(
                        {
                            "name": track_name,
                            "artist": track_artist,
                            "album": track_album,
                            "year": track_year,
                            "num_tracks": album_total,
                            "num": track_num,
                            "playlist_num": offset + 1,
                            "cover": cover,
                            "genre": genre,
                            "spotify_id": spotify_id,
                            "track_url": None,
                        }
                    )
                    offset += 1
                    songs_fetched += 1
                    progress.update(
                        task_id=track_info_task,
                        description=f"Fetching track info for \n{track_name}",
                        advance=1,
                    )

                progress.update(
                    task_id=songs_task,
                    description=f"Fetched {songs_fetched} of {total_songs} songs from the playlist",
                    advance=100,
                    total=total_songs,
                )
                if total_songs == offset:
                    break

    elif item_type == "album":
        with Progress() as progress:
            album_songs_task = progress.add_task(
                description="Fetching songs from the album.."
            )
            while True:
                album_info = sp.album(album_id=item_id)
                items = sp.album_tracks(album_id=item_id, offset=offset)
                total_songs = items.get("total")
                track_album = album_info.get("name")
                track_year = (
                    album_info.get("release_date")[:4]
                    if album_info.get("release_date")
                    else ""
                )
                album_total = album_info.get("total_tracks")
                if len(album_info["images"]) > 0:
                    cover = album_info["images"][0]["url"]
                else:
                    cover = None
                if (
                    len(sp.artist(artist_id=album_info["artists"][0]["uri"])["genres"])
                    > 0
                ):
                    genre = sp.artist(artist_id=album_info["artists"][0]["uri"])[
                        "genres"
                    ][0]
                else:
                    genre = ""
                for item in items["items"]:
                    track_name = item.get("name")
                    track_artist = ", ".join(
                        [artist["name"] for artist in item["artists"]]
                    )
                    track_num = item["track_number"]
                    spotify_id = item.get("id")
                    songs_list.append(
                        {
                            "name": track_name,
                            "artist": track_artist,
                            "album": track_album,
                            "year": track_year,
                            "num_tracks": album_total,
                            "num": track_num,
                            "track_url": None,
                            "playlist_num": offset + 1,
                            "cover": cover,
                            "genre": genre,
                            "spotify_id": spotify_id,
                        }
                    )
                    offset += 1

                progress.update(
                    task_id=album_songs_task,
                    description=f"Fetched {offset} of {album_total} songs from the album {track_album}",
                    advance=offset,
                    total=album_total,
                )
                if album_total == offset:
                    break

    elif item_type == "track":
        items = sp.track(track_id=item_id)
        track_name = items.get("name")
        album_info = items.get("album")
        track_artist = ", ".join([artist["name"] for artist in items["artists"]])
        if album_info:
            track_album = album_info.get("name")
            track_year = (
                album_info.get("release_date")[:4]
                if album_info.get("release_date")
                else ""
            )
            album_total = album_info.get("total_tracks")
        track_num = items["track_number"]
        spotify_id = items["id"]
        if len(items["album"]["images"]) > 0:
            cover = items["album"]["images"][0]["url"]
        else:
            cover = None
        if len(sp.artist(artist_id=items["artists"][0]["uri"])["genres"]) > 0:
            genre = sp.artist(artist_id=items["artists"][0]["uri"])["genres"][0]
        else:
            genre = ""
        songs_list.append(
            {
                "name": track_name,
                "artist": track_artist,
                "album": track_album,
                "year": track_year,
                "num_tracks": album_total,
                "num": track_num,
                "playlist_num": offset + 1,
                "cover": cover,
                "genre": genre,
                "track_url": None,
                "spotify_id": spotify_id,
            }
        )

    return songs_list


def default_filename(**kwargs):
    """name without number"""
    return sanitize(
        f"{kwargs['artist']} - {kwargs['name']}", "#"
    )  # youtube-dl automatically replaces with #


def check_file_size_hook(d):
    # d is the dictionary containing information about the downloaded file
    file_size_threshold = (
        6 * 1024 * 1024
    )  # Set your desired threshold in bytes (e.g., 100 MB)

    if d.get("downloaded_bytes") and d["downloaded_bytes"] > file_size_threshold:
        raise Exception(
            f"File size exceeded the threshold of {file_size_threshold} bytes. Skipping to the next song."
        )


def set_tags(temp, filename, kwargs):
    """
     sets song tags after they are downloaded
    :param temp: contains index used to obtain more info about song being editted
    :param filename: location of song whose tags are to be editted
    :param kwargs: a dictionary of extra arguments to be used in tag editing
    """
    song = kwargs["track_db"][int(temp[-1])]
    try:
        song_file = MP3(filename, ID3=EasyID3)
    except mutagen.MutagenError as e:
        print(
            f"Failed to download: {filename}, please ensure YouTubeDL is up-to-date. "
        )

        return
    song_file["date"] = song.get("year")
    if kwargs["keep_playlist_order"]:
        song_file["tracknumber"] = str(song.get("playlist_num"))
    else:
        song_file["tracknumber"] = (
            str(song.get("num")) + "/" + str(song.get("num_tracks"))
        )

    song_file["genre"] = song.get("genre")
    song_file.save()
    song_file = MP3(filename, ID3=ID3)
    cover = song.get("cover")
    if cover is not None:
        if cover.lower().startswith("http"):
            req = urllib.request.Request(cover)
        else:
            raise ValueError from None
        with urllib.request.urlopen(req) as resp:  # nosec
            song_file.tags["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=resp.read(),
            )
    song_file.save()


def write_tracks(tracks_file, song_dict):
    """
    Writes the information of all tracks in the playlist[s] to a text file in csv kind of format
    This includins the name, artist, and spotify URL. Each is delimited by a comma.
    :param tracks_file: name of file towhich the songs are to be written
    :param song_dict: the songs to be written to tracks_file
    """
    track_db = []

    with open(tracks_file, "w+", encoding="utf-8", newline="") as file_out:
        i = 0
        writer = csv.writer(file_out, delimiter=";")
        for url_dict in song_dict["urls"]:
            # for track in url_dict['songs']:
            for track in url_dict["songs"]:
                track_url = track["track_url"]  # here
                track_name = track["name"]
                track_artist = track["artist"]
                track_num = track["num"]
                track_album = track["album"]
                track["save_path"] = url_dict["save_path"]
                track_db.append(track)
                track_index = i
                i += 1
                csv_row = [
                    track_name,
                    track_artist,
                    track_url,
                    str(track_num),
                    track_album,
                    str(track_index),
                ]
                try:
                    writer.writerow(csv_row)
                except UnicodeEncodeError:
                    print(
                        "Track named {track_name} failed due to an encoding error. This is \
                        most likely due to this song having a non-English name."
                    )
    return track_db


def download_songs(**kwargs):
    """
    Downloads songs from the YouTube URL passed to either current directory or download_directory, as it is passed.  [made small typo change]
    :param kwargs: keyword arguments to be passed on between functions when downloading
    """
    reference_file = DOWNLOAD_LIST
    track_db = write_tracks(reference_file, kwargs["songs"])
    os.rename(reference_file, kwargs["output_dir"] + "/" + reference_file)
    reference_file = str(kwargs["output_dir"]) + "/" + reference_file
    kwargs["reference_file"] = reference_file
    kwargs["track_db"] = track_db
    if kwargs["multi_core"] > 1:
        multicore_find_and_download_songs(kwargs)
    else:
        find_and_download_songs(kwargs)
    os.remove(reference_file)


def multicore_find_and_download_songs(kwargs):
    """
    function handles divinding songs to be downloaded among the specified number of CPU's
    extra songs are shared among the CPU's
    each cpu then handles its own batch through the multihandler fn
    """
    reference_file = kwargs["reference_file"]
    lines = []
    with open(reference_file, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)
    cpu_count = kwargs["multi_core"]
    number_of_songs = len(lines)
    songs_per_cpu = number_of_songs // cpu_count
    extra_songs = number_of_songs % cpu_count

    cpu_count_list = []
    for cpu in range(cpu_count):
        songs = songs_per_cpu
        if cpu < extra_songs:
            songs = songs + 1
        cpu_count_list.append(songs)

    index = 0
    file_segments = []
    for cpu in cpu_count_list:
        right = cpu + index
        segment = lines[index:right]
        index = index + cpu
        file_segments.append(segment)

    processes = []
    segment_index = 0
    for segment in file_segments:
        p = multiprocessing.Process(
            target=multicore_handler, args=(segment_index, segment, kwargs.copy())
        )
        processes.append(p)
        segment_index += 1

    for p in processes:
        p.start()
    for p in processes:
        p.join()


def multicore_handler(segment_index, segment, kwargs):
    """
    function to handle each unique processor spawned download job
    :param segment_index: to be used for naming the reference file to be used for processor's download batch
    :param segment: list of songs to be downloaded using spawning processor
    """
    reference_filename = f"{segment_index}.txt"
    with open(reference_filename, "w+", encoding="utf-8") as file_out:
        for line in segment:
            file_out.write(line)

    kwargs["reference_file"] = reference_filename
    find_and_download_songs(kwargs)

    if os.path.exists(reference_filename):
        os.remove(reference_filename)


def find_and_download_songs(kwargs):
    """
    function handles actual download of the songs
    the youtube_search lib is used to search for songs and get best url
    :param kwargs: dictionary of key value arguments to be used in download
    """
    sponsorblock_postprocessor = []
    reference_file = kwargs["reference_file"]
    files = {}
    with open(reference_file, "r", encoding="utf-8") as file:
        for line in file:
            temp = line.split(";")
            name, artist, album, i = (
                temp[0],
                temp[1],
                temp[4],
                int(temp[-1].replace("\n", "")),
            )

            query = f"{artist} - {name} Lyrics".replace(":", "").replace('"', "")
            print(f"Initiating download for {query}.")
            file_name = kwargs["file_name_f"](
                name=name,
                artist=artist,
                track_num=kwargs["track_db"][i].get("playlist_num"),
            )

            if kwargs["use_sponsorblock"][0].lower() == "y":
                sponsorblock_postprocessor = [
                    {
                        "key": "SponsorBlock",
                        "categories": ["skip_non_music_sections"],
                    },
                    {
                        "key": "ModifyChapters",
                        "remove_sponsor_segments": ["music_offtopic"],
                        "force_keyframes": True,
                    },
                ]
            save_path = kwargs["track_db"][i]["save_path"]
            file_path = path.join(save_path, file_name)

            mp3file_path = f"{file_path}.mp3"

            if save_path not in files:
                path_files = set()
                files[save_path] = path_files
            else:
                path_files = files[save_path]

            path_files.add(f"{file_name}.mp3")

            if (
                kwargs["no_overwrites"]
                and not kwargs["skip_mp3"]
                and path.exists(mp3file_path)
            ):
                print(f"File {mp3file_path} already exists, we do not overwrite it ")
                continue

            outtmpl = f"{file_path}.%(ext)s"
            ydl_opts = {
                "proxy": kwargs.get("proxy"),
                "default_search": "ytsearch",
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "quiet": False,
                "postprocessors": sponsorblock_postprocessor,
                "ffmpeg_location": "/usr/bin/ffmpeg",
                "progress_hooks": [check_file_size_hook],
                "noplaylist": True,
                "no_color": False,
                "postprocessor_args": [
                    "-metadata",
                    "title=" + name,
                    "-metadata",
                    "artist=" + artist,
                    "-metadata",
                    "album=" + album,
                ],
            }
            if not kwargs["skip_mp3"]:
                mp3_postprocess_opts = {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
                ydl_opts["postprocessors"].append(mp3_postprocess_opts.copy())
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([query])
                except Exception as e:
                    # log.debug(e)
                    print(e)
                    continue
            if not kwargs["skip_mp3"]:
                set_tags(temp, mp3file_path, kwargs)
        if kwargs["remove_trailing_tracks"] == "y":
            for save_path in files:
                for f in os.listdir(save_path):
                    if f not in files[save_path]:
                        print(f"File {f} is not in the playlist anymore, we delete it")
                        os.remove(path.join(save_path, f))


def master_download(urls):
    # urls = ["https://open.spotify.com/playlist/0nHlT93zRZwbtQ0p87zAaY"] example
    url_data = {"urls": []}
    for url in urls:
        url_dict = {}
        item_type, item_id = parse_spotify_url(url)
        directory_name = get_item_name(sp, item_type, item_id)
        url_dict["save_path"] = Path(
            PurePath.joinpath(Path(OUTPUT_DIR), Path(directory_name))
        )
        url_dict["save_path"].mkdir(parents=True, exist_ok=True)
        url_dict["songs"] = fetch_tracks(sp, item_type, item_id)
        url_data["urls"].append(url_dict.copy())

    download_songs(
        songs=url_data,
        output_dir=OUTPUT_DIR,
        format_str="bestaudio/best",
        skip_mp3=False,  # convert downloaded songs to mp3
        keep_playlist_order=False,
        no_overwrites=True,
        remove_trailing_tracks="no",
        use_sponsorblock="no",
        file_name_f=default_filename,
        multi_core=1,
        proxy="",
    )
