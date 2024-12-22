import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re
import os
# ------------------------------------------------------------
client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']

client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                      client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp

# ------------------------------------------------------------
def get_responses(playlist_url:str)->list:
    """
    - Takes a playlist-URL from Spotify
    - Returns raw-data response from Spotify API
    """
    # Use regex to extract playlist-id from URL
    # (part behind "playlist/..." up until potential "?")
    match = re.search(r"playlist/([^?]*)", playlist_url)
    playlist_id = match.group(1)

    # Get first response without offset
    response = sp.playlist_items(playlist_id,
                                offset=0)

    # Make new list of responses and add first response
    responses = [response]

    # Check total playlist-length and
    # infer number of necessary API-calls
    Nresponses = response['total']//100

    # If playlist longer than 100
    # perform multiple API-calls:
    for i in range(Nresponses):
        # Get new response
        response = sp.playlist_items(playlist_id,
                                    offset=(i+1)*100)
        # Append new response to list
        responses.append(response)

    # Return list of responses
    return responses


# ------------------------------------------------------------
def get_track_info(item:dict)->list:
    """
    - Takes an item from the raw-response (=dictionary)
    - Extracts the necessary track-information
    - Returns list containing track-information
    """
    track_info = []
    # ----- ----- ----- ----- ----- ----- 
    track = item['track']
    # Track name
    track_info.append(track['name'])
    # Track duration in ms
    track_info.append(track['duration_ms'])
    # Track number on album
    track_info.append(track['track_number'])
    # Track popularity
    track_info.append(track['popularity'])
    # Is track explicit
    track_info.append(track['explicit'])
    # Spotify Track ID
    track_info.append(track['id'])
    # Spotify Track URL
    track_info.append(track['external_urls']['spotify'])

    # ----- ----- ----- ----- ----- ----- 
    artist = track['artists'][0]
    # Artists name
    track_info.append(artist['name'])
    # Spotify Artist ID
    track_info.append(artist['id'])
    # Spotify Artist URL
    track_info.append(artist['external_urls']['spotify'])

    # ----- ----- ----- ----- ----- ----- 
    album = track['album']
    # Album cover in 640px
    track_info.append(album['images'][0]['url'])
    # Album name
    track_info.append(album['name'])
    # Total tracks on album
    track_info.append(album['total_tracks'])
    # Album release date
    track_info.append(album['release_date'])
    # Spotify Album ID
    track_info.append(album['id'])

    return track_info


# ------------------------------------------------------------
def get_playlist_df(responses:list)->pd.DataFrame:
        # Initialize column names for dataframe
        cols = ['track_name','track_duration_ms','track_number','track_popularity','track_explicit','track_id','track_url',
                'artist_name','artist_id','artist_url',
                'album_image','album_name','album_total_tracks','album_release_date','album_id']

        # Initialize datframe with columns
        playlist_df = pd.DataFrame(columns=cols)

        # Go through all responses
        for response in responses:
                # Make sublist from current response,
                # containing all necessary info from playlist
                sublist = [get_track_info(item) for item in response['items']]
                # Add sublist to dataframe
                playlist_df = pd.concat([playlist_df,
                                        pd.DataFrame(sublist,columns=cols)],
                                        axis=0)

        # Index is not correct after the loop - rebuild it
        playlist_df = playlist_df.reset_index(drop=True)

        # Format numerical columns
        playlist_df = playlist_df.astype({'track_duration_ms':int,
                                          'track_number':int,
                                          'track_popularity':int,
                                          'track_explicit':bool,
                                          'album_total_tracks':int})
    
        # Format data-column
        playlist_df['album_release_date'] = pd.to_datetime(playlist_df['album_release_date'],
                                                           format='mixed')

        # Return dataframe
        return playlist_df


# ------------------------------------------------------------
def playlist_to_df(playlist_url:str)->pd.DataFrame:
    """
    - Takes Spotify-Playlist-URL
    - Returns playlist-information as pd.DataFrame
    """
    # Get raw-responses from Spotify WebAPI
    responses = get_responses(playlist_url)
    # Make DataFrame from raw-responses
    playlist_df = get_playlist_df(responses)
    # Return DataFrame
    return playlist_df