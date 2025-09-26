from .base import db

class Matchday(db.Model):
    __tablename__ = 'matchdays'
    matchday_id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'), nullable=False)
    matchday_no = db.Column(db.Integer, nullable=False)
    leg = db.Column(db.Integer, nullable=False)
    date_option_1 = db.Column(db.Date)
    date_option_2 = db.Column(db.Date)

    # Relationships
    tournament = db.relationship('Tournament', backref='matches', lazy=True)

    @property
    def date_option_1_str(self):
        return self.matchday.date_option_1.strftime('%a, %b %d') if self.date_option_1 else None

    @property
    def date_option_2_str(self):
        return self.matchday.date_option_2.strftime('%a, %b %d') if self.date_option_2 else None

    @property
    def date_options_str(self):
        return self.date_option_1_str + ' - ' + self.date_option_2_str