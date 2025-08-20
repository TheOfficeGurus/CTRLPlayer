from flask import Flask
from app.config import Config
from app.models import init_db
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    Config.getconf()
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] =Config.__database__
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
        
    register_blueprints(app)
    return app