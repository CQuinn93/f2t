import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from app.models.goal_scored import GoalScored

db = SQLAlchemy()
flask_bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.environ['f2t_pg_user']}:{os.environ['f2t_pg_pw']}"
                                             f"@{os.environ['f2t_pg_host']}/{os.environ['f2t_pg_db']}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    flask_bcrypt.init_app(app)

    return app
