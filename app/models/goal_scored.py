from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class GoalScored(db.Model):
    __table_args__ = {"schema": "app"}

    goal_scored_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer)
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    created_on = db.Column(db.DateTime, server_default='NOW()')

    def __repr__(self):
        return f"<GoalScored {self.goal_scored_id}, {self.first_name}, {self.created_on}>"

    def to_dict(self):
        return {'goal_scored_id': self.goal_scored_id, 'player_id': self.player_id, 'first_name': self.first_name,
                'second_name': self.second_name, 'created_on': self.created_on}
