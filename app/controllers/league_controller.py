from flask import Blueprint, jsonify, make_response, request

from app import db
from app.models.league import League

league_main = Blueprint('league_main', __name__)


@league_main.route('', methods=['GET', 'POST'])
def goal_scored():
    """
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
    league = League(user_id=user_id, name=name)
    db.session.add(league)
    db.session.commit()

    # Return success message
    return jsonify(status='success',
                   data={'GoalScored': league.to_dict()})
