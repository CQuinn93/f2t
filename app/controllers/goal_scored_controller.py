import json

from flask import Blueprint, make_response, request

from app import db
from app.models.goal_scored import GoalScored

goal_scored_main = Blueprint('main', __name__)


@goal_scored_main.route('/test_model', methods=['GET', 'POST'])
def goal_scored():
    """
    """
    if request.method == 'GET':
        return get_goal_scored(request)
    elif request.method == 'POST':
        return post_goal_scored(request)
    else:
        response_object = {
            'message': 'Must use GET or POST for HTTP methods'
        }
        return json.dumps(response_object, 405)


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
    response_json = json.dumps([ob.to_dict() for ob in goal_scored_records], default=str)
    response = make_response(response_json)
    response.headers['Content-Type'] = 'application/json'
    return response


def post_goal_scored(req):
    """
    """
    # Get data from request
    req.get_data()
    player_id = req.json.get('player_id')
    first_name = req.json.get('first_name')
    second_name = req.json.get('second_name')

    # Create instance of GoalScored and add to database
    gs = GoalScored(player_id=player_id, first_name=first_name, second_name=second_name)
    db.session.add(gs)
    db.session.commit()

    # Return success message
    response_object = {
        'status': 'success - USERS NOT ADDED TO DB YET, TESTING APP',
          'data': {'GoalScored': gs.to_dict()}
    }
    return response_object, 200
