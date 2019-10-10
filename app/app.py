from flask import Flask
from flask import request
import json
import psycopg2
import secrets as sec

app = Flask(__name__)


@app.route('/')
def home():
    return "online"


@app.route('/user/')
def get_users():
    # Get user id supplied
    user_id = request.args.get('user_id')

    # Create query based on user id supplied in request, if any
    query = "SELECT * FROM app.user"
    if user_id is not None:
        # Update query to return only the user specified
        query = query + " WHERE user_id = " + user_id

    # Setup connection
    conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
        sec.db, sec.user, sec.pw, sec.host))

    # Retrieve user data
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    # return json.
    return app.response_class(
        response=json.dumps(results, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run()
