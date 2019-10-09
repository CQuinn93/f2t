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
    # conn = psycopg2.connect("dbname=" + secrets.db + " user=" + secrets.user +
    # " password=" + secrets.pw + " host=" + secrets.host)
    conn = psycopg2.connect("dbname={} user={} password={} host={}".format(sec.db, sec.user, sec.pw, sec.host))

    # Retrieve user data
    cur = conn.cursor()
    cur.execute("SELECT * FROM app.user")
    results = cur.fetchall()

    cur.close()
    conn.close()
    var1 = 'A'
    var2 = 'B'

    return json.dumps("a{}_b{}".format(var1, var2), indent=4, sort_keys=True, default=str)


if __name__ == '__main__':
    app.run()
