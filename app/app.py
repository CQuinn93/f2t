from flask import Flask
import json
import psycopg2
import secrets as sec

app = Flask(__name__)


@app.route('/')
def home():
    return "online"


@app.route('/users')
def get_users():
    # Setup connection
    conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
        sec.db, sec.user, sec.pw, sec.host))

    # Retrieve user data
    cur = conn.cursor()
    cur.execute("SELECT * FROM app.user")
    results = cur.fetchall()

    cur.close()
    conn.close()

    return json.dumps(results, indent=4, sort_keys=True, default=str)


if __name__ == '__main__':
    app.run()
