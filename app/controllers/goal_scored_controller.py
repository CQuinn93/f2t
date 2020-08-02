from flask import Blueprint, jsonify, request

from app import db
from app.models.goal_scored import GoalScored

goal_scored_main = Blueprint('goal_scored_main', __name__)


@goal_scored_main.route('', methods=['GET', 'POST'])
def goal_scored():
    """
    """
    if request.method == 'GET':
        return get_goal_scored(request)
    elif request.method == 'POST':
        return post_goal_scored(request)
    else:
        # Requests that are not GET or POST can't make it this far but handle this scenario anyway
        return jsonify(status='failed', message='Must use GET or POST for HTTP methods.'), 450


def get_goal_scored(req):
    """
    """
    player_id = req.args.get('player_id')

    # Get all records with this player_id if supplied, otherwise get all records
    if player_id:
        goal_scored_records = GoalScored.query.filter_by(player_id=player_id).all()
    else:
        goal_scored_records = GoalScored.query.all()

    # Return records found as json - empty array if no records found
    return jsonify([ob.to_dict() for ob in goal_scored_records])


def post_goal_scored(req):
    """
    """
    # Get data from request
    req.get_data()
    player_id = req.json.get('player_id')
    first_name = req.json.get('first_name')
    second_name = req.json.get('second_name')

    # Create instance of GoalScored and add to database
    new_goal_scored = GoalScored(player_id=player_id, first_name=first_name, second_name=second_name)
    db.session.add(new_goal_scored)
    db.session.commit()

    # Return success message
    return jsonify(status='success', data={'GoalScored': new_goal_scored.to_dict()})
