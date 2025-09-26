# management_routes.py (Example Blueprint)
from flask import Blueprint, render_template, request, jsonify
from datetime import date
from sqlalchemy.orm import joinedload
from models import db, Tournament, Team, Matchday, Match, MatchStatus

management_bp = Blueprint("management", __name__, url_prefix="/manage")


# --- 1. Route to Load the Management Page ---
@management_bp.route("/")
def tournaments_management():
    # Pass all existing data for initial setup
    all_tournaments = Tournament.query.all()
    all_teams = Team.query.order_by(Team.name).all()

    # We pass the default MatchStatus for template logic
    return render_template(
        "tournaments_management.html",
        tournaments=all_tournaments,
        teams=all_teams,
        MatchStatus=MatchStatus,
    )


# --- 2. AJAX Endpoint to Load Matchdays for a Selected Tournament ---
@management_bp.route("/matchdays/<int:tournament_id>")
def get_matchdays_for_tournament(tournament_id):
    # Load all matchdays and their associated matches in one query to optimize performance
    matchdays = (
        Matchday.query.filter_by(tournament_id=tournament_id)
        .options(joinedload(Matchday.matches))
        .order_by(Matchday.leg, Matchday.matchday_no)
        .all()
    )

    # Render *only* the matchday list partial
    return render_template(
        "_matchdays_list.html",
        matchdays=matchdays,
        tournament_id=tournament_id,
        teams=Team.query.order_by(Team.name).all(),
        MatchStatus=MatchStatus,
    )
