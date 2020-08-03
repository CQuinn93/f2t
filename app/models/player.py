from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):
    __table_args__ = {"schema": "app"}

    player_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    goals_scored = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, server_default='NOW()')

    def __repr__(self):
        return f"<Player {self.player_id}, {self.first_name}, {self.created_on}>"

    def to_dict(self):
        return {'player_id': self.player_id, 'first_name': self.first_name, 'second_name': self.second_name,
                'created_on': self.created_on}
