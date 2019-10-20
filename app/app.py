from flask import Flask
from flask import request
import json
import psycopg2
import secrets as sec

app = Flask(__name__)


# Helper functions
def simple_query(query):
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
        sec.db, sec.user, sec.pw, sec.host))

    # Retrieve data
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result


@app.route('/')
def home():
    return "online"


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


if __name__ == '__main__':
    app.run()
