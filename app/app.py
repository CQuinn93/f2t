from flask import Flask
from flask import request
from flask_bcrypt import Bcrypt
from psycopg2 import errors
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
    # Setup connection - details stored in environment variables
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


def execute_query_with_values(pre_values_query, values, post_values_query='',
                              values_format='(%s,%s)'):
    """
    """
    # Setup connection to database
    conn, cur = con_to_app_db()

    # Construct query
    values_psql = values_to_psql(cur, values, values_format)
    query = pre_values_query + ' ' + values_psql + '' + post_values_query

    # Catch common database related errors and return message to caller
    try:
        cur.execute(query)
    except errors.ForeignKeyViolation as e:
        # Foreign Key violated when trying to insert team or team_member,
        # return error message
        print(e)
        results = '{"psycopg2.errors.ForeignKeyViolation": "' + str(e) + '"}'
        return app.response_class(
            response=json.dumps(results, indent=4, sort_keys=True, default=str),
            status=422,
            mimetype='application/json'
        )
    except errors.NotNullViolation as e:
        # A null value was supplied for a column that does not allow null
        # values - most likely user did not supply league_id or user_id
        print(e)
        results = '{"psycopg2.errors.NotNullViolation": "' + str(e) + '"}'
        return app.response_class(
            response=json.dumps(results, indent=4, sort_keys=True, default=str),
            status=422,
            mimetype='application/json'
        )

    conn.commit()
    cur.close()
    conn.close()

    return query


def con_to_app_db():
    # Setup connection - details stored in environment variables
    conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
        os.environ['f2t_pg_db'], os.environ['f2t_pg_user'],
        os.environ['f2t_pg_pw'], os.environ['f2t_pg_host']))

    cur = conn.cursor()

    return conn, cur


def values_to_psql(cursor, values, f='(%s,%s)'):
    return ','.join(cursor.mogrify(f, x).decode("utf-8") for x in values)


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


@app.route('/team/', methods=['GET', 'POST'])
def team():
    if request.method == 'GET':
        return get_team(request)
    elif request.method == 'POST':
        return post_team(request)
    else:
        return app.response_class(
            response=None,
            status=405,
            mimetype='application/json'
        )


def get_team(req):
    # Get user id argument
    user_id = req.args.get('user_id')

    # Simple select to get team data
    query = """
    SELECT  t.team_id
            ,t.user_id
            ,tm.team_member_id
            ,p.player_id
            ,p.first_name
            ,p.second_name
      FROM  app.team t
        INNER JOIN  app.team_member tm
            ON      t.team_id = tm.team_id
        INNER JOIN  app.player p
            ON      p.player_id = tm.player_id
    """

    # Update query to return a team if specified
    if user_id:
        query = query + " WHERE user_id = " + user_id

    results = simple_query(query)

    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


def post_team(req):
    # Get data from request
    req.get_data()
    league_id = req.json.get('league_id')
    user_id = req.json.get('user_id')
    player_ids = tuple(req.json.get('player_ids'))

    # Convert all player ids into strings for easier formatting
    player_ids = tuple([[str(x)] for x in player_ids])

    # Create query to insert team and team members in a single statement
    pre_values_query = f"""
        with new_team as (
          insert into app.team (user_id, league_id)
          values ({user_id}, {league_id})
          returning team_id
        )
        insert into app.team_member (team_id, player_id)
        values
    """

    # Send insert query to
    resp = execute_query_with_values(pre_values_query, player_ids,
                                     values_format="((select * from new_team), %s)")

    if isinstance(resp, type(app.response_class())):
        return resp
    else:
        result = '{"team_added": True}'
        return app.response_class(
            response=json.dumps(result, indent=4, sort_keys=True, default=str),
            status=200,
            mimetype='application/json'
        )


@app.route('/player/')
def get_players():
    # Get player id argument
    player_id = request.args.get('player_id')

    # Simple select to get all users
    query = "SELECT * FROM app.player"

    # Update query to return a player if specified
    if player_id:
        query = query + " WHERE player_id = " + player_id

    results = simple_query(query)

    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


@app.route('/league/')
def get_leagues():
    # Get league id argument
    league_id = request.args.get('league_id')

    # Simple select to get all users
    query = "SELECT * FROM app.league"

    # Update query to return a league if specified
    if league_id:
        query = query + " WHERE league_id = " + league_id

    results = simple_query(query)

    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run()
