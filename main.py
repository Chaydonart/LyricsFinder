import requests
from bs4 import BeautifulSoup
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

# Clés API
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
GENIUS_API_TOKEN = os.getenv('GENIUS_API_TOKEN')

# Authentification avec Spotify
auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
spotify = Spotify(auth_manager=auth_manager)

# Fonction pour rechercher des paroles sur Genius
def search_lyrics_on_genius(lyrics):
    headers = {'Authorization': f'Bearer {GENIUS_API_TOKEN}'}
    search_url = f'https://api.genius.com/search?q={lyrics}'
    response = requests.get(search_url, headers=headers)
    response_data = response.json()
    
    songs = []
    for hit in response_data['response']['hits']:
        songs.append({
            'title': hit['result']['title'],
            'artist': hit['result']['primary_artist']['name'],
            'genius_url': hit['result']['url'],
            'song_id': hit['result']['id']
        })
    
    return songs


def get_lyrics_from_musixmatch(artist, title):
    api_key = os.getenv('MUSIXMATCH_API_TOKEN')
    base_url = "https://api.musixmatch.com/ws/1.1"
    endpoint = f"{base_url}/matcher.lyrics.get"

    params = {
        "q_track": title,
        "q_artist": artist,
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    if data['message']['header']['status_code'] == 200:
        lyrics = data['message']['body']['lyrics']['lyrics_body']
        return lyrics

    return "Les paroles ne peuvent pas être récupérées pour cette chanson."

# Fonction pour trouver des chansons sur Spotify
def search_song_on_spotify(title, artist):
    query = f'{title} {artist}'
    results = spotify.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'spotify_url': track['external_urls']['spotify'],
            'preview_url': track['preview_url']
        }
    return None

    # Rechercher le moment spécifique dans les paroles
    index = lyrics.lower().find(moment.lower())
    if index == -1:
        return "Moment spécifié non trouvé dans les paroles."
    
    # Extraire un extrait centré autour du moment spécifique
    start_index = max(0, index - excerpt_length // 2)
    end_index = min(len(lyrics), index + excerpt_length // 2)
    excerpt = lyrics[start_index:end_index]
    
    return excerpt

# Fonction principale pour rechercher des paroles et associer les chansons Spotify
def find_song_by_lyrics(lyrics):
    songs = search_lyrics_on_genius(lyrics)
    results = []
    for song in songs:
        spotify_song = search_song_on_spotify(song['title'], song['artist'])
        if spotify_song:
            lyrics_text = get_lyrics_from_musixmatch(song['artist'], song['title'])
            song.update(spotify_song)
            song['lyrics'] = lyrics_text
            results.append(song)
    return results

# Exemple d'utilisation
lyrics_searched = input("Entrez les paroles que vous recherchez : ")
print(f"Recherche en cours...")
songs = find_song_by_lyrics(lyrics_searched)
for i, song in enumerate(songs, start=1):
    print(f"Chanson {i}:")
    print(f"Titre: {song['title']}, Artiste: {song['artist']}")
    print(f"URL Spotify: {song['spotify_url']}, URL de prévisualisation: {song['preview_url']}")
    print(f"URL Genius: {song['genius_url']}")
    # print(f"Lyrics : {song['lyrics']}")
    print("\n")