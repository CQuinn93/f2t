from flask import Blueprint, jsonify, make_response, request

from app.models.player import Player

player_main = Blueprint('player_main', __name__)


@player_main.route('', methods=['GET', 'POST'])
def get_player():
    """ Player route.
    ---
    get:
        summary: Get all players or player specified.
        description: Get a user by ID or all players if no ID is supplied.
        parameters:
            - name: player_id
              in: query
              description: Numeric ID of the player to get
              type: integer
              required: false
        responses:
            200:
                description: Player object(s) to be returned.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Player'
    """
    player_id = request.args.get('player_id')

    # Get all records with this player_id if supplied, otherwise get all records
    if player_id:
        player_records = Player.query.filter_by(player_id=player_id).all()
    else:
        player_records = Player.query.all()

    # Return records found as json - empty array if no records found
    return jsonify([ob.to_dict() for ob in player_records])
