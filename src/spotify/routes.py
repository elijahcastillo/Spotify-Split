from flask import Blueprint, redirect, session, render_template, request, url_for, jsonify, flash
bp = Blueprint("spotify", __name__)

import json
from src.helperFunc import get_All_Playlists, createPlaylist, getTracksFromPlaylist, addTrackToPlaylist, deleteTrackFromRootPlaylist, TOKIN_INFO


def protect(func):
    def wrapper():
        token_info = session.get(TOKIN_INFO, None)
        root = session.get("root", None)
        
        if not token_info:
            return redirect("/") #User has not logged in
        
        if not root:
            return redirect(url_for("spotify.chooseRootPlaylist"))

        return func()
        
    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper
        


@bp.route("/choose-root-playlist", methods=["GET", "POST"])
def chooseRootPlaylist():
    token_info = session.get(TOKIN_INFO, None)
    if not token_info:
        return redirect("/") #User has not logged in
  
    if request.method == "POST":
        #Store root playlist in session
        form = request.form
        rootID = form.get("playlist", None)
        
        if not rootID:
            flash("Please select a Playlist")
        else:
            session["root"] = rootID
            return redirect(url_for("spotify.chooseChildrenPlaylists"))
    
    list_of_playlists = get_All_Playlists()
        
    return render_template("rootPlaylist.html", playlists = list_of_playlists)



@bp.route("/choose-children-playlists", methods=["GET", "POST"])
@protect
def chooseChildrenPlaylists():
    
    list_of_playlists = get_All_Playlists()
    
    if request.method == "POST":
        form = request.form
        
        if not form:
            flash("Please select Playlist(s)")
        else:
            
            children_ids = []
            children_data = []

            #Get ids for each child playlist
            for value in form.to_dict(flat=True).values():
                children_ids.append(value)
                
            #Get data from each playlist
            for playlist in list_of_playlists:
                if playlist["id"] in children_ids:
                    children_data.append(playlist)
                        
            #Store data in session
            session["children"] = children_data
            # session["childrenId"] = children_ids
            
            return redirect(url_for("spotify.splitPlaylist"))
    
    

    root_id = session["root"]
    root_playlist = {}
    
    #remove the root playlist from children list
    for idx, playlist in enumerate(list_of_playlists):
        if playlist["id"] == root_id:
            root_playlist = list_of_playlists.pop(idx)
            
    return render_template("childrenPlaylist.html", playlists = list_of_playlists, root = root_playlist)


@bp.route("/create-new-playlist", methods=["GET", "POST"])
@protect
def createNewPlaylist():
    
    if request.method == "POST":
        form = request.form
        name = form.get("newPlaylistName")
        isPublic = bool(form.get("playlistState"))
        if(name):
            createPlaylist(name, isPublic)
            return redirect(url_for("spotify.chooseChildrenPlaylists"))
        
    return render_template("createPlaylist.html")



@bp.route("/get-tracks", methods=["POST"])
def getTracks():
    root = session["root"]
    offset = json.loads(request.data.decode('UTF-8'))["offset"]
        
    tracks = getTracksFromPlaylist(root, offset)
    return jsonify(tracks)


@bp.route("/split-playlist", methods=["GET", "POST"])
@protect
def splitPlaylist():
    
    childrenPlaylists = session.get("children", [])   

    return render_template("split.html", playlists = childrenPlaylists)




#------------- Action routes ----------------
@bp.route("/add", methods=["POST"])
def add():
    """Add current track to selected children playlists"""
    child_ids = json.loads(request.data.decode('UTF-8'))["child_ids"]
    track_uri = json.loads(request.data.decode('UTF-8'))["uri"]

    addTrackToPlaylist(child_ids, track_uri)
    return "ok"

@bp.route("/add-and-delete", methods=["POST"])
def addAndDelete():
    """Add current track to selected children playlists, delete from root playlist"""
    child_ids = json.loads(request.data.decode('UTF-8'))["child_ids"]
    position = json.loads(request.data.decode('UTF-8'))["position"]
    track_uri = json.loads(request.data.decode('UTF-8'))["uri"]

    addTrackToPlaylist(child_ids, track_uri)
    deleteTrackFromRootPlaylist(track_uri, position)
    return "ok"

@bp.route("/delete_from_root", methods=["POST"])
def deleteFromRoot():
    """ONLY DELETE track from root playlist"""
    position = json.loads(request.data.decode('UTF-8'))["position"]
    track_uri = json.loads(request.data.decode('UTF-8'))["uri"]
    
    deleteTrackFromRootPlaylist(track_uri, position)
    return "ok"
    
    
