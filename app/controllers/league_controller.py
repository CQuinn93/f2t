from flask import Blueprint, jsonify, make_response, request

from app import db
from app.models.league import League

league_main = Blueprint('league_main', __name__)


@league_main.route('', methods=['GET', 'POST'])
def league():
    """ League route.
    ---
    get:
        summary: Get leagues or league specified.
        description: Get a league(s) by league or user ID or all leagues if no league or user ID is supplied.
        parameters:
            - name: league_id
              in: query
              description: Numeric ID of the league to get
              type: integer
              required: false
            - name: user_id
              in: query
              description: Numeric ID of the user who owns the league(s) to get
              type: integer
              required: false
        responses:
            200:
                description: League object(s) to be returned.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/League'
    """
    if request.method == 'GET':
        return get_league(request)
    elif request.method == 'POST':
        return post_league(request)
    else:
        # Requests that are not GET or POST can't make it this far but handle this scenario anyway
        return jsonify(status='failed', message='Must use GET or POST for HTTP methods.'), 450


def get_league(req):
    """
    """
    league_id = req.args.get('league_id')
    user_id = req.args.get('user_id')

    # Get all records with this player_id if supplied, otherwise get all records
    if league_id:
        league_records = League.query.filter_by(league_id=league_id).all()
    elif user_id:
        league_records = League.query.filter_by(user_id=user_id).all()
    else:
        league_records = League.query.all()

    # Return records found as json - empty array if no records found
    return jsonify([ob.to_dict() for ob in league_records])


def post_league(req):
    """
    """
    # Get data from request
    req.get_data()
    user_id = req.json.get('user_id')
    name = req.json.get('name')

    # Create instance of GoalScored and add to database
    new_league = League(user_id=user_id, name=name)
    db.session.add(new_league)
    db.session.commit()

    # Return success message
    return jsonify(status='success', data={'GoalScored': new_league.to_dict()})
