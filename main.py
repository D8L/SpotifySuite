import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# load environment variables
load_dotenv()
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
spotify_redirect_url = os.environ['SPOTIPY_REDIRECT_URI']
# case by case
spotify_scope = 'user-library-read, user-library-modify, playlist-modify-private, playlist-modify-public, user-top-read'


def main():
    # print ASCII art and start main loop
    ascii_print()
    while True:
        try:
            print('''
Input 1 or 2 to select an option:
    1.) Sort your liked or playlist tracks
    2.) Put favorite tracks in a playlist''')
            input_choice = int(input('Choice: '))

            if input_choice in [1, 2]:
                sp = authenticate_user()

                if input_choice == 1:
                    # fetch user's playlists
                    playlist_return = sp.current_user_playlists()
                    chosen_playlist, playlist_length, chosen_id = choose_playlists(playlist_return)
                    playlist_results = get_playlist_items(sp, playlist_length, chosen_id)

                    # sort tracks by genre
                    unique_tracks, songs_by_genre, artist_cache, artist_ids = process_playlist_data(playlist_results,
                                                                                                    sp)
                    # create a new playlist based on selected genres
                    print_genres(songs_by_genre)
                    create_playlist_and_add_by_genre(sp, songs_by_genre)

                elif input_choice == 2:
                    # create a playlist of favorite tracks
                    song_limit, song_range = get_limit(), get_range()
                    top_tracks = sp.current_user_top_tracks(limit=song_limit, time_range=song_range)
                    create_playlist_and_add_by_favorites(sp, top_tracks)

            else:
                print("Error: Please enter the numbers 1 or 2.")

        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")


def authenticate_user():
    # authenticate the user with Spotify
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_url,
            scope=spotify_scope,
            requests_timeout=2,
            open_browser=True))
    return sp


def process_playlist_data(playlist_results, sp):
    # process playlist data to sort tracks by genre
    unique_tracks = set()
    songs_by_genre = {}
    artist_cache = {}
    artist_ids = set()

    for track in playlist_results:
        track_uri = track['track']['uri']
        if track_uri not in unique_tracks:
            unique_tracks.add(track_uri)
            primary_artist = track['track']['artists'][0]
            artist_id = primary_artist['id']
            if artist_id is not None:
                artist_ids.add(artist_id)

    # fetch artist information for all unique artist IDs
    batch_size = 50
    artist_ids = list(artist_ids)  # convert to a list for batch processing

    for i in range(0, len(artist_ids), batch_size):
        batch_ids = artist_ids[i:i + batch_size]

        # make a batch request to the API to fetch artist information for all unique IDs in the batch
        batch_artist_info = sp.artists(artists=batch_ids)

        # update the artist_cache with the fetched information
        for artist_info in batch_artist_info['artists']:
            artist_id = artist_info['id']
            artist_cache[artist_id] = artist_info

    # process the tracks with the artist information and group them by genre
    for track in playlist_results:
        primary_artist = track['track']['artists'][0]
        artist_id = primary_artist['id']

        if artist_id in artist_cache:
            artist_info = artist_cache[artist_id]
            artist_genres = artist_info['genres']

            for genre in artist_genres:
                if genre not in songs_by_genre:
                    songs_by_genre[genre] = []
                songs_by_genre[genre].append(track['track']['uri'])  # - important - come back to this!

    return unique_tracks, songs_by_genre, artist_cache, artist_ids


def get_playlist_details():
    # get user input for playlist name and visibility (if applicable)
    playlist_name = name_playlist()
    playlist_visibility = get_playlist_visibility()
    return playlist_name, playlist_visibility


def create_playlist_and_add_by_genre(sp, songs_by_genre):
    genre_choice = input('''
Separate each genre you want to sort with a comma and a space
(e.g., rap, synthpop, jazz, new wave, chicago blues): ''')
    playlist_name, playlist_visibility = get_playlist_details()
    selected_genres = genre_choice.lower().split(', ')

    separator = ', '
    result_string = separator.join(selected_genres)

    # create a new playlist based on selected genres above and add tracks to it
    playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, (playlist_visibility == 1), False,
                                       description=result_string)
    playlist_id = playlist['id']
    matching_tracks = []

    for genre in selected_genres:
        if genre in songs_by_genre:
            matching_tracks.extend(songs_by_genre[genre])

    unique_tracks = list(set(matching_tracks))
    total_tracks = len(unique_tracks)

    for i in range(0, total_tracks, 100):
        segment = unique_tracks[i:i + 100]
        sp.playlist_add_items(playlist_id, segment)

    print("\nPlaylist created!\n")


def create_playlist_and_add_by_favorites(sp, top_tracks):
    playlist_name, playlist_visibility = get_playlist_details()
    playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, (playlist_visibility == 1), False, "")
    playlist_id = playlist['id']
    track_uris = [item['uri'] for item in top_tracks.get('items', [])]
    sp.playlist_add_items(playlist_id, track_uris)
    print("\nPlaylist created!\n")


def get_limit():
    # get the number of songs (1-50) to be pulled
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


def name_playlist():
    while True:
        option = input('''
What would you like to name the playlist: ''')
        if 100 > len(option) > 0:
            return option
        else:
            print("Error: Please enter a valid playlist name.")


def choose_playlists(playlist_return):
    print('''
Input the number associated with the playlist you want to sort:''')
    for index, playlist in enumerate(playlist_return['items'], start=1):
        print(f"\t{index}.) {playlist['name']}")
    chosen_playlist = playlist_return['items'][(int(input('Choice: ')) - 1)]
    print()
    playlist_length = chosen_playlist['tracks']['total']
    chosen_id = chosen_playlist['id']
    return chosen_playlist, playlist_length, chosen_id


def get_playlist_items(sp, playlist_length, chosen_id):
    playlist_results = []
    print(f"Extracting genres from {playlist_length} songs...")
    for i in range(0, playlist_length, 100):
        playlist_batch = sp.playlist_items(chosen_id, limit=100, offset=i, market=None,
                                           additional_types=['track'], )
        for item in playlist_batch['items']:
            playlist_results.append(item)

    return playlist_results


def print_genres(songs_by_genre):
    print("Genre choices:")
    genres = sorted(songs_by_genre.keys())
    num_columns = 4

    # calculate the maximum width for each column
    max_width = max(len(genre) for genre in genres)

    # calculate the number of rows needed based on the number of columns
    num_rows = (len(genres) + num_columns) // num_columns

    # iterate through the rows and columns
    for row in range(num_rows):
        for col in range(num_columns):
            index = row + col * num_rows
            if index < len(genres):
                genre = genres[index]
                # use string formatting to ensure consistent column width
                print("\t{:<{width}}".format(genre, width=max_width), end="\t")
        print()  # move to the next row


def ascii_print():
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
