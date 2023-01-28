from flask import Blueprint, redirect, session, render_template, request, url_for
bp = Blueprint("main", __name__)


from src.helperFunc import create_Spotify_Oauth, get_token, TOKIN_INFO


@bp.route("/")
def index():
    return render_template("home.html")


@bp.route("/login")
def login():
    spotify_Oauth = create_Spotify_Oauth()
    
    #Send user to spotify to authenticate the app
    auth_url = spotify_Oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")



#The endpoint Oauth will redirect to after authorization
@bp.route("/redirect")
def redirectPage():
    spotify_Oauth = create_Spotify_Oauth()
    session.clear()
    
    #spotify redirects to this page with a url arg that contatins auth code
    auth_code = request.args.get("code")
    
    #With that code get  ( access token, refresh token, token expiration date)  from spotify
    token_info = spotify_Oauth.get_access_token(auth_code)
    
    session[TOKIN_INFO] = token_info
    return redirect(url_for("spotify.chooseRootPlaylist", _external=True))
