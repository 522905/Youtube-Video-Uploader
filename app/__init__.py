from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app
