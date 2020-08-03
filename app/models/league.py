from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class League(db.Model):
    __table_args__ = {"schema": "app"}

    league_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    created_on = db.Column(db.DateTime, server_default='NOW()')

    def __repr__(self):
        return f"<League {self.league_id}, {self.user_id}, {self.name}, {self.created_on}>"

    def to_dict(self):
        return {'league_id': self.league_id, 'user_id': self.user_id, 'name': self.name, 'created_on': self.created_on}
