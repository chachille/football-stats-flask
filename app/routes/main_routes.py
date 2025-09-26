from flask import render_template, Flask, Blueprint, request
from app.models.base import db
from app.models.matchday import Matchday
from app.models.match import Match
from app.models.team import Team
from app.models.match import MatchStatus
from app.models.tournament import Tournament
from datetime import date
from sqlalchemy import asc, func, case, and_, or_

main_bp = Blueprint('main', __name__)


# Get Last Matchday
def get_last_matchday(tournament_id):
    today = date.today()

    if tournament_id:
        # Get next matchday with matches scheduled after today for the selected Tournament
        last_matchday = (
            Matchday.query
            .join(Match)
            .filter(Match.datetime <= today, Matchday.tournament_id == tournament_id)
            .order_by(Match.datetime.desc())
            .first())
        print(f"Matchday {last_matchday}")
    else:
        # Get next matchday with matches scheduled after today for the all Tournaments
        last_matchday = (
            Matchday.query
            .join(Match)
            .filter(Match.datetime <= today)
            .order_by(Match.datetime.desc())
            .first())
        
    if last_matchday:
        matchdays = [last_matchday]
    else:
        matchdays = []
    
    print(f"Length of matchdays: {len(matchdays)}")
    return matchdays


# Get Last and Next Matchdays
def get_last_next_matchday(tournament_id):
    today = date.today()

    if tournament_id:
        # Get last and next matchday with matches scheduled after today for the selected Tournament
        last_matchday = (
            Matchday.query
            .join(Match)
            .filter(Match.datetime <= today, Matchday.tournament_id == tournament_id)
            .order_by(Match.datetime.desc())
            .first())
        next_matchday = (
            Matchday.query
            .join(Match)
            .filter(Match.datetime >= today, Matchday.tournament_id == tournament_id)
            .order_by(Match.datetime)
            .first())
        print(f"Next Matchday {next_matchday}")
    else:
        # Get last and next matchday with matches scheduled after today for all Tournaments
        last_matchday = (
            Matchday.query
            .join(Match)
            .filter(Match.datetime <= today)
            .order_by(Match.datetime.desc())
            .first())
        next_matchday = (
            Matchday.query
            .join(Match)
            .filter(Match.datetime >= today)
            .order_by(Match.datetime)
            .first())    
        
    if last_matchday and next_matchday:
        matchdays = [last_matchday, next_matchday]
    else:
        matchdays = []
    
    print(f"Length of matchdays: {len(matchdays)}")
    return matchdays

# Get Next Matchday Matches
def get_last_matchday_matches(tournament_id):
    today = date.today()

    # Get next matchday with matches scheduled after today
    next_matchday = (
        Matchday.query
        .join(Match)
        .filter(Match.datetime >= today, Matchday.tournament_id == tournament_id)
        .order_by(Match.datetime)
        .first()
    )

    matches = []
    if next_matchday:
        matches = (
            Match.query
            .filter_by(matchday_id=next_matchday.matchday_id)
            .order_by(Match.datetime, Match.match_id)
            .all()
        )

    return matches

# Get All Matches
def get_all_matches():
    matches = []
    matches = (Match.query.order_by(Match.datetime, Match.match_id).all())

    return matches

# Get Matchdays Count
def get_matchdays_count():
    matchdays_count = 0
    matchdays_count = Matchday.query.count()
    return matchdays_count

# Get Matchdays by Tournament
def get_all_matchdays(tournament_id):
    matchdays = []
    if tournament_id:
        matchdays = (Matchday.query.filter(Matchday.tournament_id == tournament_id).order_by(Matchday.matchday_no).all())
    else:
        matchdays = (Matchday.query.order_by(Matchday.matchday_no).all())
    return matchdays

# Get Matches by Matchday
def get_all_matches_by_matchday(matchday_id):
    matches = []
    if matchday_id:
        matches = (Match.query.filter(Matchday.matchday_id == matchday_id).order_by(Match.datetime, Match.match_id).all())

# Get Matches By Team
def get_all_matches_by_team(team_id):
    matches = []
    print(f"get_all_matches_by_team - Team ID: {team_id}")
    if team_id:
        matches = (Match.query
                   .filter(or_(Match.home_team_id == team_id,  Match.away_team_id == team_id))
                   .order_by(Match.datetime, Match.match_id).all())
    return matches


# Get Current Standings Filtered By Tournament
def get_current_standings_by_tournament(tournament_id):
    # Points calculation (already done)
    points_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 3),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 3),
        ((Match.home_score == Match.away_score), 1),
        else_=0)

    # Wins
    wins_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 1),
        else_=0)

    # Draws
    draws_case = case(
        (Match.home_score == Match.away_score, 1),
        else_=0)

    # Losses
    losses_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score < Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score < Match.home_score), 1),
        else_=0)

    # Goals For (GF)
    goals_for_case = case(
        (Match.home_team_id == Team.team_id, Match.home_score),
        (Match.away_team_id == Team.team_id, Match.away_score),
        else_=0
    )

    # Goals Against (GA)
    goals_against_case = case(
        (Match.home_team_id == Team.team_id, Match.away_score),
        (Match.away_team_id == Team.team_id, Match.home_score),
        else_=0
    )

    print(f"tournament_id: {tournament_id}")
    standings = (
        Team.query
        .outerjoin(
            Match,
            ((Match.home_team_id == Team.team_id) | (Match.away_team_id == Team.team_id))
            & (Match.status == "PLAYED") & (Match.tournament_id == tournament_id)
        )
        .with_entities(
            Team.name,
            func.sum(points_case).label("points"),
            func.sum(wins_case).label("W"),
            func.sum(draws_case).label("D"),
            func.sum(losses_case).label("L"),
            func.sum(goals_for_case).label("GF"),
            func.sum(goals_against_case).label("GA"),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).label("GD"),
        )
        .group_by(Team.name)
        .order_by(
            func.sum(points_case).desc(),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).desc(),
            func.sum(goals_for_case).desc()
        )
        .all()
    )

    return standings


# Get Current Standings
def get_current_standings():
    # Points calculation (already done)
    points_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 3),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 3),
        ((Match.home_score == Match.away_score), 1),
        else_=0)

    # Wins
    wins_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 1),
        else_=0)

    # Draws
    draws_case = case(
        (Match.home_score == Match.away_score, 1),
        else_=0)

    # Losses
    losses_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score < Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score < Match.home_score), 1),
        else_=0)

    # Goals For (GF)
    goals_for_case = case(
        (Match.home_team_id == Team.team_id, Match.home_score),
        (Match.away_team_id == Team.team_id, Match.away_score),
        else_=0
    )

    # Goals Against (GA)
    goals_against_case = case(
        (Match.home_team_id == Team.team_id, Match.away_score),
        (Match.away_team_id == Team.team_id, Match.home_score),
        else_=0
    )

    standings = (
        Team.query
        .outerjoin(
            Match,
            ((Match.home_team_id == Team.team_id) | (Match.away_team_id == Team.team_id))
            & (Match.status == "PLAYED")
        )
        .with_entities(
            Team.name,
            func.sum(points_case).label("points"),
            func.sum(wins_case).label("W"),
            func.sum(draws_case).label("D"),
            func.sum(losses_case).label("L"),
            func.sum(goals_for_case).label("GF"),
            func.sum(goals_against_case).label("GA"),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).label("GD"),
        )
        .group_by(Team.name)
        .order_by(
            func.sum(points_case).desc(),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).desc(),
            func.sum(goals_for_case).desc()
        )
        .all()
    )
     
    return standings


@main_bp.route('/')
def home():
    tournaments = Tournament.query.all()
    teams = Team.query.all()

    return render_template('base.html', tournaments=tournaments, teams=teams)


# Endpoint for the dynamic content
@main_bp.route('/content/<page>')
def get_content(page):
    tournament_id = request.args.get('tournament_id')
    team_id = request.args.get('team_id')
    print(f"get_content / request team_id - Team ID: {team_id}")
    
    if tournament_id and tournament_id.isdigit():
        tournament_id = int(tournament_id)
    else:
        tournament_id = None # Handles 'all' or no selection

    if team_id and team_id.isdigit():
        team_id = int(team_id)
        team = Team.query.get(team_id)
    else:
        team_id = None # Handles 'all' or no selection

    if page == 'overview':
        # Fetch data for the overview page
        matchdays = get_last_next_matchday(tournament_id)
        standings = get_current_standings_by_tournament(tournament_id)
        # Render ONLY the overview content partial
        return render_template('overview.html', matchdays=matchdays, team_id=None, standings=standings, MatchStatus=MatchStatus)
    elif page == 'matches':
        # If team_id is provided, fetch data for selected team matches
        if team_id:
            matches = get_all_matches_by_team(team_id)
            return render_template('matches_all.html', team=team, matches=matches, MatchStatus=MatchStatus)
        else: # Fetch data for selected tournament matches
            matchdays = get_all_matchdays(tournament_id)
            return render_template('matches_all.html', matchdays=matchdays, team_id=team_id, MatchStatus=MatchStatus)

    # Add a fallback for unknown pages
    return "Page not found", 404



@main_bp.route('/overview')
def overview():
    today = date.today()

    # Get next matchday with matches scheduled after today
    next_matchday = (
        Matchday.query
        .join(Match)
        .filter(Match.datetime <= today)
        .order_by(Match.datetime.desc())
        .first()
    )

    matches = []
    if next_matchday:
        matches = (
            Match.query
            .filter_by(matchday_id=next_matchday.matchday_id)
            .order_by(Match.datetime, Match.match_id)
            .all()
        )

    # Points calculation (already done)
    points_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 3),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 3),
        ((Match.home_score == Match.away_score), 1),
        else_=0)

    # Wins
    wins_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 1),
        else_=0)

    # Draws
    draws_case = case(
        (Match.home_score == Match.away_score, 1),
        else_=0)

    # Losses
    losses_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score < Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score < Match.home_score), 1),
        else_=0)

    # Goals For (GF)
    goals_for_case = case(
        (Match.home_team_id == Team.team_id, Match.home_score),
        (Match.away_team_id == Team.team_id, Match.away_score),
        else_=0
    )

    # Goals Against (GA)
    goals_against_case = case(
        (Match.home_team_id == Team.team_id, Match.away_score),
        (Match.away_team_id == Team.team_id, Match.home_score),
        else_=0
    )

    standings = (
        Team.query
        .outerjoin(
            Match,
            ((Match.home_team_id == Team.team_id) | (Match.away_team_id == Team.team_id))
            & (Match.status == "PLAYED")
        )
        .with_entities(
            Team.name,
            func.sum(points_case).label("points"),
            func.sum(wins_case).label("W"),
            func.sum(draws_case).label("D"),
            func.sum(losses_case).label("L"),
            func.sum(goals_for_case).label("GF"),
            func.sum(goals_against_case).label("GA"),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).label("GD"),
        )
        .group_by(Team.name)
        .order_by(
            func.sum(points_case).desc(),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).desc(),
            func.sum(goals_for_case).desc()
        )
        .all()
    )

    return render_template('overview.html', active_page='overview', matches=matches, standings=standings)



@main_bp.route('/matches_all')
def matches_list():
    return render_template('matches_all.html')


@main_bp.route('/standings_all')
def standings_all():
    return render_template('overview.html')     ### CHANGE THAT !!!! FOR TEST ONLY !!!!


@main_bp.route('/data_management')
def data_management():
    return render_template('base.html')



@main_bp.route('/overview_old')
def overview_old():
    today = date.today()

    # Get next matchday with matches scheduled after today
    next_matchday = (
        Matchday.query
        .join(Match)
        .filter(Match.datetime <= today)
        .order_by(Match.datetime.desc())
        .first()
    )

    matches = []
    if next_matchday:
        matches = (
            Match.query
            .filter_by(matchday_id=next_matchday.matchday_id)
            .order_by(Match.datetime, Match.match_id)
            .all()
        )

    # Generate standings dynamically from Match data
    # standings = (
    #     Team.query
    #     .outerjoin(Match, ((Match.home_team_id == Team.team_id) | (Match.away_team_id == Team.team_id)) & (Match.status == 'FT'))
    #     .with_entities(
    #         Team.name,
    #         func.sum(
    #             func.case([
    #                 ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 3),
    #                 ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 3),
    #                 ((Match.home_score == Match.away_score), 1)
    #             ], else_=0)                
    #         ).label('points')
    #     )
    #     .group_by(Team.name)
    #     .order_by(func.sum(
    #         func.case([
    #             ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 3),
    #             ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 3),
    #             ((Match.home_score == Match.away_score), 1)
    #         ], else_=0)
    #     ).desc())
    #     .all()
    # )

    # Points calculation (already done)
    points_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 3),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 3),
        ((Match.home_score == Match.away_score), 1),
        else_=0)

    # Wins
    wins_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score > Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score > Match.home_score), 1),
        else_=0)

    # Draws
    draws_case = case(
        (Match.home_score == Match.away_score, 1),
        else_=0)

    # Losses
    losses_case = case(
        ((Match.home_team_id == Team.team_id) & (Match.home_score < Match.away_score), 1),
        ((Match.away_team_id == Team.team_id) & (Match.away_score < Match.home_score), 1),
        else_=0)

    # Goals For (GF)
    goals_for_case = case(
        (Match.home_team_id == Team.team_id, Match.home_score),
        (Match.away_team_id == Team.team_id, Match.away_score),
        else_=0
    )

    # Goals Against (GA)
    goals_against_case = case(
        (Match.home_team_id == Team.team_id, Match.away_score),
        (Match.away_team_id == Team.team_id, Match.home_score),
        else_=0
    )

    standings = (
        Team.query
        .outerjoin(
            Match,
            ((Match.home_team_id == Team.team_id) | (Match.away_team_id == Team.team_id))
            & (Match.status == "PLAYED")
        )
        .with_entities(
            Team.name,
            func.sum(points_case).label("points"),
            func.sum(wins_case).label("W"),
            func.sum(draws_case).label("D"),
            func.sum(losses_case).label("L"),
            func.sum(goals_for_case).label("GF"),
            func.sum(goals_against_case).label("GA"),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).label("GD"),
        )
        .group_by(Team.name)
        .order_by(
            func.sum(points_case).desc(),
            (func.sum(goals_for_case) - func.sum(goals_against_case)).desc(),
            func.sum(goals_for_case).desc()
        )
        .all()
    )


    return render_template('matches.html', matches=matches, matchday_no=next_matchday.matchday_no if next_matchday else None, standings=standings)