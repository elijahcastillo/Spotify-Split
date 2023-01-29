from flask import session, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os


CLIENT_ID=os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
TOKIN_INFO=os.getenv('TOKIN_INFO')

#Check if access token is expired, if so, use refresh token to get new access token
def get_token():
    token_info = session.get(TOKIN_INFO, None)
    
    if not token_info:
        return redirect("/") #User has not logged in
    
    #Check access token expiration
    now = int(time.time())
    is_expired = token_info["expires_at"] - now < 60
    

    if is_expired:
        spotify_Oauth = create_Spotify_Oauth()
        refresh_token = token_info["refresh_token"]
        token_info = spotify_Oauth.refresh_access_token(refresh_token) #Get new access token
        
    return token_info
        
        
def get_All_Playlists():
    token_info = get_token()
    
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_playlists = sp.current_user_playlists(limit=50)["items"]
     
    list_of_playlist = []
    
    for playlist in user_playlists:
        name = playlist["name"]
        
        try:
            img_url = playlist["images"][0]["url"]
        except IndexError:
            #Playlist has no Image
            img_url = url_for("static", filename='assets/noMusic.png') #Provide Default
            
        id = playlist["id"]


        
        dic = {
            "name": name,
            "url": img_url,
            "id": id
        }
        
        list_of_playlist.append(dic)
        
    return list_of_playlist


def createPlaylist(name, isPublic):
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_id = sp.current_user()["id"]
    
    sp.user_playlist_create(user_id, name, isPublic)
    
    
def getTracksFromPlaylist(root_id, offset):
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    output = []

    tracks = sp.playlist_tracks(root_id, offset=offset ,limit=20)["items"]
    

    for idx, value in enumerate(tracks):
        name = value["track"]["name"]
        artist = value["track"]["artists"][0]["name"]
        album_url = value["track"]["album"]["images"][0]["url"]
        album_name = value["track"]["album"]["name"]
        release_date = value["track"]["album"]["release_date"]
        duration = value["track"]["duration_ms"]
        mp3_url = value["track"]["preview_url"]
        uri = value["track"]["uri"]
        
        
        song = {
            "title": name,
            "artist": artist,
            "album_url": album_url,
            "album_name": album_name,
            "mp3_url": mp3_url,
            "track_uri": uri,
            "release_date": release_date,
            "duration": duration,
            "index": idx
        }
        
        output.append(song)
    

    return output

    
    
# Action Functions
def addTrackToPlaylist(playlistIds, trackId):
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_id = sp.current_user()["id"]
    
    #Loop over each selected playlist and add the track from root
    for playlist in playlistIds:
        sp.user_playlist_add_tracks(user_id, playlist, [trackId])
        
        
def deleteTrackFromRootPlaylist(trackId, position):
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    root = session["root"]
    items = [{"uri": trackId, "positions": [position]}]
    
    sp.playlist_remove_specific_occurrences_of_items(root, items)



def create_Spotify_Oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("main.redirectPage", _external=True),
        scope="user-library-read user-read-recently-played user-read-playback-state playlist-modify-private playlist-modify-public"
    )