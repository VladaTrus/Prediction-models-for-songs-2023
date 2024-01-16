import json
import os
import re
from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

ENG_FILENAME = 'lyrics_eng_fin.json'
OTH_FILENAME = 'lyrics_other_fin.json'

nltk.download('stopwords')

def extract_bracket_contents(text):
    """ Extract contents within brackets """
    return re.findall(r'\[([^\]]+)\]', text)

def tokenize_and_count(expressions):
    """ Tokenize expressions and count occurrences of each token """
    tokens = [token for expr in expressions for token in word_tokenize(expr)]
    return Counter(tokens)

def clean_tokenize(expressions):
    """ Tokenize expressions, remove non-letters and stopwords """
    stop_words = set(stopwords.words('english'))
    tokens = []
    for expr in expressions:
        words = word_tokenize(expr)
        for word in words:
            if word.isalpha() and word.lower() not in stop_words:
                tokens.append(word.lower())
    return tokens

def process_lyrics(data):
    all_tokens = Counter()

    for song_id, song_data in data.items():
        lyrics = song_data.get('lyrics', '')
        expressions = extract_bracket_contents(lyrics)
        tokens = clean_tokenize(expressions)
        all_tokens.update(tokens)    
    return all_tokens

def process_data(counter, data, n=15):
    words = [word for word, _ in counter.most_common(n)]

    pattern = r'\[\s*[^]]*(?:' + '|'.join(words) + r')[^]]*\]'

    for song_id, song_data in data.items():
        lyrics = song_data.get('lyrics', '')
        clean_lyrics = re.sub(pattern, '', lyrics, flags=re.IGNORECASE)
        song_data['lyrics'] = clean_lyrics

def load_from_json(filename):
    """Load data from a JSON file."""
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    else:
        return {}

def save_to_json(filename, data):
        """Save data to a JSON file."""
        with open(filename, 'w') as json_file:
            json.dump(data, json_file)

def main():
    eng_tracks = load_from_json(ENG_FILENAME)
    other_tracks = load_from_json(OTH_FILENAME)

    eng_common = process_lyrics(eng_tracks)
    process_data(eng_common, eng_tracks)

    oth_common = process_lyrics(other_tracks)
    process_data(oth_common, other_tracks)
    
    save_to_json(ENG_FILENAME, eng_tracks)
    save_to_json(OTH_FILENAME, other_tracks)

if __name__ == "__main__":
    main()
