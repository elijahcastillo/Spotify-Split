from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "9rnchw54khs9kdnvmsldw"
    app.config["SESSION_COOKIE_NAME"] = "Eli's Cookie"
    
    #Blueprints
    from src.main.routes import bp as main_bp
    from src.spotify.routes import bp as spotify_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(spotify_bp)
    
    return app