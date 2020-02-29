from flask import Flask
from flask import request
from flask_bcrypt import Bcrypt
import json
import os
import psycopg2

app = Flask(__name__)
f_bcrypt = Bcrypt(app)


# Helper functions
def simple_query(query, commit=False, get_result=True):
    """Runs an SQL query against the database and returns the result

    Parameters
    ----------
    query : str
        The SQL query to get results for

    Returns
    -------
    list
        a list of tuples where each tuple is a row returned by the query
    """
    # Setup connection
    conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
        os.environ['f2t_pg_db'], os.environ['f2t_pg_user'],
        os.environ['f2t_pg_pw'], os.environ['f2t_pg_host']))

    # Retrieve data
    cur = conn.cursor()
    cur.execute(query)

    if commit:
        conn.commit()

    if get_result:
        result = cur.fetchall()
    else:
        result = None

    cur.close()
    conn.close()

    return result


@app.route('/')
def home():
    return "online"


@app.route('/register', methods=['POST'])
def register():
    data = request.form.to_dict()
    pw_hash = f_bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Create new entry in user table first then account table
    query = """
    WITH row AS (
    INSERT INTO app.user (username, email, created_on)
    VALUES ('{}', '{}', NOW()) RETURNING username
    )
    INSERT INTO app.account (username, hashed_password, created_on)
    SELECT username, '{}', NOW()
    FROM row
    ;
    """.format(data['username'], data['email'], pw_hash)

    simple_query(query, commit=True, get_result=False)

    result = "{'registered': True}"

    return app.response_class(
        response=json.dumps(result, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


@app.route('/user/')
def get_users():
    # Get user id argument
    user_id = request.args.get('user_id')

    # Simple select to get all users
    query = "SELECT * FROM app.user"

    # Update query to return a user if specified
    if user_id:
        query = query + " WHERE user_id = " + user_id

    results = simple_query(query)

    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


@app.route('/team/')
def get_team():
    # Get user id argument
    user_id = request.args.get('user_id')

    # Simple select to get team data
    query = """
    SELECT t.team_id, t.user_id, tm.team_member_id, p.player_id, p.name,
           p.objective_met
    FROM app.team t
    INNER JOIN app.team_member tm
      ON t.team_id = tm.team_id
    INNER JOIN app.player p
      ON p.player_id = tm.player_id
    """

    # Update query to return a user if specified
    if user_id:
        query = query + " WHERE user_id = " + user_id

    results = simple_query(query)

    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


@app.route('/player/')
def get_players():
    # Get player id argument
    player_id = request.args.get('player_id')

    # Simple select to get all users
    query = "SELECT * FROM app.player"

    # Update query to return a user if specified
    if player_id:
        query = query + " WHERE player_id = " + player_id

    results = simple_query(query)

    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run()
