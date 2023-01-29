from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')
    
    #Blueprints
    from src.main.routes import bp as main_bp
    from src.spotify.routes import bp as spotify_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(spotify_bp)
    
    return app