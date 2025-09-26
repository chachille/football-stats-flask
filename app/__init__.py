from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.models.base import db
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)    
    app.config.from_object('config.Config')

    print(app.config['SQLALCHEMY_DATABASE_URI'])
    
    db.init_app(app)
    # migrate.init_app(app, db)

    #with app.app_context():
    #    from . import routes  # Import routes here to avoid circular imports
    #    db.create_all()  # Create database tables for our data models
    
    register_blueprints(app)

    return app