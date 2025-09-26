from .base import db
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum as PgEnum, ForeignKey

class MatchStatus(PyEnum):
    SCHEDULED = 0
    PLAYED = 1
    POSTPONED = 2
    CANCELED = 3


# --- Models ---
class Match(db.Model):
    __tablename__ = 'matches'
    match_id = db.Column(db.Integer, primary_key=True)
    matchday_id = db.Column(db.Integer, db.ForeignKey('matchdays.matchday_id'), nullable=False)
    datetime = db.Column(db.DateTime)
    venue = db.Column(db.String(100))
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    status = db.Column(PgEnum(MatchStatus), default=MatchStatus.SCHEDULED)

    # Relationships
    matchday = db.relationship('Matchday', backref='matches', lazy=True)
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_matches')

    # Properties

    # Result and Score methods for a team_id based on status
    def result_icon(self, team_id):
        # Font Awesome Icons
        win_icon = '<i class="fas fa-check-circle win-icon" title="Win"></i>'
        draw_icon = '<i class="fas fa-minus-circle draw-icon" title="Draw"></i>'
        loss_icon = '<i class="fas fa-times-circle loss-icon" title="Loss"></i>'
        if self.status != MatchStatus.PLAYED:
            return ""
        else:
            if self.home_score == self.away_score:
                result = draw_icon
            elif self.home_score > self.away_score:
                result = win_icon if team_id == self.home_team_id else loss_icon
            elif self.home_score < self.away_score:
                result = win_icon if team_id == self.away_team_id else loss_icon
            return result

    def result_score(self, team_id):
        if self.status != MatchStatus.PLAYED:
            return ""
        else:
            return f"{self.home_score}-{self.away_score}"

    @property
    def datetime_str(self):
        return self.datetime.strftime('%a, %b %d') if self.datetime else None

    @property
    def tournament_id(self):
        return self.matchday.tournament_id if self.tournament_id else None

    @property
    def matchday_number(self):
        return self.matchday.matchday_no if self.matchday_no else None

    @property
    def home_team_name(self):
        return self.home_team.name if self.home_team else 'Unknown'

    @property
    def away_team_name(self):
        return self.away_team.name if self.away_team else 'Unknown'
