from .base import db

class Team(db.Model):
    __tablename__ = 'teams'

    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships
    #players = db.relationship('Player', backref='team', lazy=True)
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', back_populates='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', back_populates='away_team', lazy=True)
    tournament_entries = db.relationship('TournamentTeam', lazy=True)

    def __repr__(self):
        return f"<Team {self.name}>"
