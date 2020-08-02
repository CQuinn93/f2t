import json
import os

from flask import Flask
from flask import request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from psycopg2 import errors
import psycopg2


app = Flask(__name__)
DB_URI = (f"postgresql://{os.environ['f2t_pg_user']}:{os.environ['f2t_pg_pw']}"
          f"@{os.environ['f2t_pg_host']}/{os.environ['f2t_pg_db']}")
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db = SQLAlchemy(app)
f_bcrypt = Bcrypt(app)


# Helper functions
def simple_query(query, commit=False, get_result=True):
    """Execute an SQL query on the database.

    Parameters
    ----------
    query : str
        The SQL query to get results for
    commit : bool
        Whether the query should be committed on the database after execution
    get_result : bool
        Whether the result of the query should be requested

    Returns
    -------
    list of tuples
        Each row returned from executing the query is represented by a tuple in
        the list. Each column value is a separate element in the tuple. None is
        returned if `get_result` is set to False.
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


def execute_query_with_values(values_query, values, post_values_query='',
                              values_format='(%s,%s)'):
    """Formats an SQL query containing the `VALUES` command and executes on the
    database.

    This function is intended to be used when multiple rows are to be inserted
    into the database. The values supplied are added to the query in a format
    that is understood by the database.

    Parameters
    ----------
    values_query : str
        The SQL query which contains the `VALUES` command
    values : tuple of (str,)
        The raw values to be used by the `VALUES` command
    post_values_query : str
        Any SQL to be appended to `values_query` (the default is a blank string
        which means no additional SQL is appended to the query)
    values_format : str
        The format the values should follow in the SQL query

    Returns
    -------
    tuple of (str, `flask.wrappers.Response`)
        str: The query sent to the database to execute.
        `flask.wrappers.Response`: A response containing the error while
            executing the query on the database (None if no error occurred).
    """
    # Setup connection to database
    conn, cur = con_to_app_db()

    # Construct query
    values_psql = values_to_psql(cur, values, values_format)
    query = values_query + ' ' + values_psql + '' + post_values_query

    # Catch common database related errors and return message to caller
    try:
        cur.execute(query)
    except errors.ForeignKeyViolation as e:
        # Foreign Key violated, most likely trying to insert team or
        # team_member, return error message
        print(e)
        results = '{"psycopg2.errors.ForeignKeyViolation": "' + str(e) + '"}'
        response = app.response_class(
            response=json.dumps(results, indent=4, sort_keys=True, default=str),
            status=422,
            mimetype='application/json'
        )
        return query, response
    except errors.NotNullViolation as e:
        # A null value was supplied for a column that does not allow null
        # values - most likely user did not supply league_id or user_id
        print(e)
        results = '{"psycopg2.errors.NotNullViolation": "' + str(e) + '"}'
        response = app.response_class(
            response=json.dumps(results, indent=4, sort_keys=True, default=str),
            status=422,
            mimetype='application/json'
        )
        return query, response

    conn.commit()
    cur.close()
    conn.close()

    return query, None


def con_to_app_db():
    """Create a connection to the database and opens a cursor that uses this
    connection.

    Returns
    -------
    tuple of (`psycopg2.extensions.connection`, `psycopg2.extensions.cursor`,)
        `psycopg2.extensions.connection`: The connection object to the database.
        `psycopg2.extensions.cursor`: A cursor opened using the connection in
            the first element of this tuple.
    """
    # Setup connection - details stored in environment variables
    conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
        os.environ['f2t_pg_db'], os.environ['f2t_pg_user'],
        os.environ['f2t_pg_pw'], os.environ['f2t_pg_host']))

    cur = conn.cursor()

    return conn, cur


def values_to_psql(cursor, values, format_='(%s,%s)'):
    """Returns a query string for the `VALUE` containing the `values` supplied
     in the `f`ormat supplied.

    Parameters
    ----------
    cursor : `psycopg2.extensions.connection`
        A cursor opened on a connection to a database
    values : tuple of (str,)
        The raw values to be used by the `VALUES` command
    format_ : str
        The format of the values for the SQL query

    Returns
    -------
    str
        The values supplied formatted to fit into a `VALUE` command in an SQL
        query.
    """
    return ','.join(cursor.mogrify(format_, x).decode("utf-8") for x in values)


@app.route('/')
def home():
    """ Root route to test if API is online.
    ---
    get:
        summary: Root endpoint.
        description: Returns a simple string - used to test if API is online.
        responses:
            200:
                description: Returns string "online".
    """
    return "online"


@app.route('/register', methods=['POST'])
def register():
    """ Register route.
    ---
    post:
        summary: Adds a new user to the database.
        description: Adds a new user entry and a new account entry to the
            database. Accounts are used for authenticating requests and users
            are used for getting information about a user.
        requestBody:
            description: Contains the data associated to this user. This
                includes an email, a username, and a password.
            required: true
            content:
                multipart/form-data:
                    schema:
                        $ref: '#/components/schemas/User'
        responses:
            200:
                description: JSON string indicating successful registration.
    """
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
    """ User route.
    ---
    get:
        summary: Get users or user specified.
        description: Get a user by ID or all users if no ID is supplied.
        parameters:
            - name: user_id
              in: query
              description: Numeric ID of the user to get
              type: integer
              required: false
        responses:
            200:
                description: User object(s) to be returned.
    """
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
    """ Team route.
    ---
    get:
        summary: Get all teams or a specific team.
        description: Get a user by ID or all users if no ID is supplied. A team
            consists of all team members and player data for each team member.
        parameters:
            - name: team_id
              in: query
              description: User ID
              type: integer
              required: false
        responses:
            200:
                description: Team object(s) to be returned.
    post:
        summary: Add a new team to the database.
        description: Adds a new team entry and many new team_member entries to
            the database.
        requestBody:
            description: Contains the data associated to this team. This
                includes the league, user (owner), and player id(s).
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Team'
                        ## TODO: Create Team schema, should include the
                        ## TODO: following:
                        ## TODO:    - league_id: ID of League this team
                        ## TODO:                 belongs to.
                        ## TODO:    - user_id: ID of owner (user) of this team.
                        ## TODO:    - player_ids: List of IDs of players that
                        ## TODO:                  are part of this team.
                        ## TODO: This will be added in a future story.
        responses:
            200:
                description: JSON string indicating team as added successfully.
            422:
                description: If the team data was formatted correctly but the
                    data failed a database rule this code will be returned with
                    the error message from the database. The most common
                    reasons for failure are (1) when one of the requestBody
                    values (league, user, and/or player id) supplied does not
                    exists in the database (ForeignKeyViolation error) or (2)
                    when a null/missing value is supplied for one of the
                    requestBody values (NotNullViolation error).
    """
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
    values_query = f"""
        with new_team as (
          insert into app.team (user_id, league_id)
          values ({user_id}, {league_id})
          returning team_id
        )
        insert into app.team_member (team_id, player_id)
        values
    """

    # Send insert query to
    format_values = "((select * from new_team), %s)"
    results = execute_query_with_values(values_query, player_ids,
                                        values_format=format_values)

    if isinstance(results[1], type(app.response_class())):
        return results[1]
    else:
        result = '{"team_added": True}'
        return app.response_class(
            response=json.dumps(result, indent=4, sort_keys=True, default=str),
            status=200,
            mimetype='application/json'
        )


@app.route('/league/')
def get_leagues():
    """ League route.
    ---
    get:
        summary: Get leagues or league specified.
        description: Get a league by ID or all leagues if no ID is supplied.
        parameters:
            - name: league_id
              in: query
              description: Numeric ID of the league to get
              type: integer
              required: false
        responses:
            200:
                description: League object(s) to be returned.
    """
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
