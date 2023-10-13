import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
spotify_redirect_url = os.environ['SPOTIPY_REDIRECT_URI']
spotify_scope = os.environ['SPOTIPY_SCOPE']


def main():
    ascii()
    sp = authenticate_user()

    while True:
        try:
            print('''
Input 1 or 2 to select an option:
    1.) Sort your liked or playlist tracks
    2.) Put favorite tracks in a playlist''')
            input_choice = int(input('Choice: '))
            if input_choice in [1, 2]:
                if input_choice == 1:

                    # fetches information to proceed
                    playlist_return = sp.current_user_playlists()
                    chosen_playlist, playlist_length, chosen_id = choose_playlists(playlist_return)
                    playlist_results = get_playlist_items(sp, playlist_length, chosen_id)

                    unique_artists = set()
                    unique_genres = set()
                    print("Loading genres...")
                    for track in playlist_results:
                        for artist in track['track']['artists']:
                            print(artist)
                            artist_id = artist['id']
                            print(artist_id)
                            if artist_id is not None:
                                if artist_id not in unique_artists:
                                    unique_artists.add(artist_id)
                                    artist_info = sp.artist(artist_id=artist_id)
                                    artist_genres = artist_info['genres']
                                    for genre in artist_genres:
                                        unique_genres.add(genre)
                    print("Genre choices:")
                    for genre in unique_genres:
                        print(genre)
                    genre_search = input("What genre do you want: ")
                    playlist_name = name_playlist()
                    playlist_visibility = get_playlist_visibility()
                    playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, (playlist_visibility == 1), False,
                                                       "")
                    playlist_id = playlist['id']
                    matching_tracks = []
                    unique_track_uris = set()
                    for track in playlist_results:
                        artist_genres = set()
                        unique_track = track['track']['uri']
                        for artist in track['track']['artists']:
                            artist_id = artist['id']
                            if artist_id is not None:
                                artist_info = sp.artist(artist_id=artist_id)
                                if 'genres' in artist_info:
                                    artist_genres.update(artist_info['genres'])
                        if genre_search in artist_genres and unique_track not in unique_track_uris:
                            print(unique_track)
                            matching_tracks.append(unique_track)
                            unique_track_uris.add(unique_track)
                    total_tracks = len(matching_tracks)
                    for i in range(0, total_tracks, 100):
                        segment = matching_tracks[i:i + 100]
                        sp.playlist_add_items(playlist_id, segment)
                    if total_tracks % 100 != 0 and total_tracks > 100:
                        remaining_segment = matching_tracks[total_tracks - (total_tracks % 100):]
                        sp.playlist_add_items(playlist_id, remaining_segment)
                    print("Playlist created!")

                elif input_choice == 2:

                    limit = get_limit()
                    range1 = get_range()
                    top_tracks = get_top_tracks(sp, limit, range1)

                    playlist_name = name_playlist()
                    playlist_visibility = get_playlist_visibility()

                    playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, (playlist_visibility == 1), False,
                                                       "")
                    playlist_id = playlist['id']

                    track_uris = [item['uri'] for item in top_tracks.get('items', [])]
                    sp.playlist_add_items(playlist_id, track_uris)
                    print("\nPlaylist created!\n")

            else:
                print("Error: Please enter the numbers 1 or 2.")

        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")


def authenticate_user():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_url,
            scope=spotify_scope))
    return sp


def fetch_playlist_id(sp, playlist_name):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            print(playlist['name'])
            return playlist['id']


def get_top_tracks(sp, song_limit, song_range):
    return sp.current_user_top_tracks(song_limit, 0, song_range)


def get_limit():
    while True:
        try:
            limit = int(input('''
How many of your favorite songs would you like to pull? (1-50): '''))
            if 1 <= limit <= 50:
                return limit
            else:
                print("Error: Please enter a number between 1 and 50.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")


def get_range():
    while True:
        try:
            print('''
Input 1, 2, or 3 to select the range:
    1.) Short-term (4 weeks)
    2.) Medium-term (6 months)
    3.) Long-term (lifetime)''')
            range1 = int(input('Choice: '))
            if range1 in [1, 2, 3]:
                if range1 == 1:
                    return 'short_term'
                elif range1 == 2:
                    return 'medium_term'
                elif range1 == 3:
                    return 'long_term'
            else:
                print("Error: Please enter the numbers 1, 2, or 3.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")


def get_playlist_visibility():
    while True:
        try:
            print('''
Input 1 or 2 to select the playlist visibility:
    1.) Public
    2.) Private''')
            playlist_visibility = int(input('Choice: '))
            if playlist_visibility in [1, 2]:
                return playlist_visibility
            else:
                print("Error: Please enter the numbers 1 or 2.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")


def option_choice():
    while True:
        try:
            print('''
Input 1 or 2 to select an option:
    1.) Playlists
    2.) Liked Songs
''')
            choice = int(input('Choice: '))
            print()
            if choice in [1, 2]:
                if choice == 1:
                    return 1
                elif choice == 2:
                    return 2
            else:
                print("Error: Please enter the numbers 1 or 2.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")


def name_playlist():
    while True:
        option = input('''
What would you like to name the playlist: ''')
        if len(option) < 100:
            return option
        else:
            print("Error: Please enter a valid playlist name.")


def choose_playlists(playlist_return):
    print('''
    Input the number associated with the playlist you want to sort:''')
    for index, playlist in enumerate(playlist_return['items'], start=1):
        print(f"{index}.) {playlist['name']}")
    chosen_playlist = playlist_return['items'][(int(input('Choice: ')) - 1)]
    print()
    playlist_length = chosen_playlist['tracks']['total']
    chosen_id = chosen_playlist['id']
    return chosen_playlist, playlist_length, chosen_id

def get_playlist_items(sp, playlist_length, chosen_id):
    playlist_results = []
    print(f"Extracting data from {playlist_length} songs...")
    for i in range(0, playlist_length, 100):
        print("Batch processing...")
        playlist_batch = sp.playlist_items(chosen_id, limit=100, offset=i, market=None,
                                           additional_types=['track'])
        for item in playlist_batch['items']:
            playlist_results.append(item)
    return playlist_results


def ascii():
    ascii_text = '''
       ____           __   _  ___          ____       _  __      
      / __/___  ___  / /_ (_)/ _/__ __    / __/__ __ (_)/ /_ ___ 
     _\ \ / _ \/ _ \/ __// // _// // /   _\ \ / // // // __// -_)
    /___// .__/\___/\__//_//_/  \_, /   /___/ \_,_//_/ \__/ \__/ 
        /_/                    /___/                             
    '''
    spotify_green = "\033[38;2;30;215;96m"
    reset_color = "\033[0m"
    print(spotify_green + ascii_text + reset_color)


if __name__ == "__main__":
    main()
