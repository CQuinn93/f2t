from flask import Blueprint, jsonify, make_response, request

from app import db
from app.models.team import Team

team_main = Blueprint('team_main', __name__)


@team_main.route('', methods=['GET', 'POST'])
def team():
    """ Team route.
    ---
    get:
        summary: Get all teams or a specific team.
        description: Get a team(s) by team, league, or user ID or all teams if no team, league, or user ID is supplied.
        parameters:
            - name: team_id
              in: query
              description: Numeric ID of the team to get
              type: integer
              required: false
            - name: league_id
              in: query
              description: Numeric ID of the league who owns the team(s) to get
              type: integer
              required: false
            - name: user_id
              in: query
              description: Numeric ID of the user who owns the team(s) to get
              type: integer
              required: false
        responses:
            200:
                description: Team object(s) to be returned.
    post:
        summary: Add a new team to the database.
        description: Adds a new team entry to the database.
        requestBody:
            description: Contains the data owner (user_id) and league (league_id) associated to this team.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Team'
        responses:
            200:
                description: JSON string indicating team was added successfully.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Team'
    """
    if request.method == 'GET':
        return get_team(request)
    elif request.method == 'POST':
        return post_team(request)
    else:
        # Requests that are not GET or POST can't make it this far but handle this scenario anyway
        return jsonify(status='failed', message='Must use GET or POST for HTTP methods.'), 450


def get_team(req):
    """
    """
    team_id = req.args.get('team_id')
    league_id = req.args.get('league_id')
    user_id = req.args.get('user_id')

    # Get all records with this player_id if supplied, otherwise get all records
    if team_id:
        team_records = Team.query.filter_by(team_id=team_id).all()
    elif league_id:
        team_records = Team.query.filter_by(league_id=league_id).all()
    elif user_id:
        team_records = Team.query.filter_by(user_id=user_id).all()
    else:
        team_records = Team.query.all()

    # Return records found as json - empty array if no records found
    return jsonify([ob.to_dict() for ob in team_records])


def post_team(req):
    """
    """
    # Get data from request
    req.get_data()
    league_id = req.json.get('league_id')
    user_id = req.json.get('user_id')

    # Create instance of GoalScored and add to database
    new_team = Team(user_id=user_id, league_id=league_id)
    db.session.add(new_team)
    db.session.commit()

    # Return success message
    return jsonify(status='success', data={'Team': new_team.to_dict()})
