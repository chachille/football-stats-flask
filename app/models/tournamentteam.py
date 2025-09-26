from .base import db
from sqlalchemy import UniqueConstraint

class TournamentTeam(db.Model):
    __tablename__ = 'tournament_teams'
    tournament_team_id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

    __table_args__ = (UniqueConstraint('tournament_id', 'team_id', name='uq_tournament_team'),)