import json
import os
import pickle
import re
from langdetect import detect

def detect_language(lyrics_text, max_iterations=5):
    detected_languages = []

    for _ in range(max_iterations):
        try:
            language = detect(lyrics_text)
            detected_languages.append(language)
        except Exception as e:
            print(f"An error occurred during language detection: {e}")

    return detected_languages

def process_lyrics(songs):
    english_lyrics = {}
    other_lyrics = {}

    for track_id, data in songs.items():
        data['lyrics'] = data.pop('found_lyrics', data.get('lyrics', ''))
        data['lyrics'] = re.sub(r".*Lyrics\[?", "[", data['lyrics'])
        data['lyrics'] = re.sub(r"\d*Embed$", "", data['lyrics'])

        detected_languages = detect_language(data['lyrics'])

        # Use the most common language detected
        if detected_languages:
            most_common_language = max(set(detected_languages), key=detected_languages.count)
            print(f"Detected language for {track_id}: {most_common_language}")

            # Store lyrics based on language
            if most_common_language == 'en':
                english_lyrics[track_id] = data
            else:
                other_lyrics[track_id] = data

    return english_lyrics, other_lyrics    

def save_to_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    my_filename = 'raw_lyrics.json'
    en_filename = 'lyrics_eng_fin.json'
    other_filename = 'lyrics_other_fin.json'
    pkl_filename = 'processed_lyrics.pickle'
    
    my_filepath = os.path.join(script_dir, my_filename)
    en_filepath = os.path.join(script_dir, en_filename)
    other_filepath = os.path.join(script_dir, other_filename)
    pkl_filepath = os.path.join(script_dir, pkl_filename)

    with open(my_filepath, 'r', encoding='utf-8') as file:
        songs = json.load(file)

    # Preprocess and separate English and non-English lyrics
    english_lyrics, other_lyrics = process_lyrics(songs)

    # Save English and other lyrics to separate JSON files
    save_to_json(en_filepath, english_lyrics)
    save_to_json(other_filepath, other_lyrics)

    # Save preprocessed songs to a pickle file
    with open(pkl_filepath, 'wb') as file:
        pickle.dump(songs, file)

    print(f'English lyrics in data: {len(english_lyrics)}')
    print(f'Lyrics in other languages in data: {len(other_lyrics)}')

if __name__ == "__main__":
    main()
