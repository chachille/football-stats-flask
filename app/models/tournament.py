from .base import db

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    tournament_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)