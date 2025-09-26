from flask import Flask
from .main_routes import main_bp

def register_blueprints(app: Flask):
    app.register_blueprint(main_bp)
