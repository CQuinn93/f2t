from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Team(db.Model):
    __table_args__ = {"schema": "app"}

    team_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    league_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100))
    created_on = db.Column(db.DateTime, server_default='NOW()')

    def __repr__(self):
        return f"<Team {self.team_id}, {self.user_id}, {self.league_id}, {self.name}, {self.created_on}>"

    def to_dict(self):
        return {'team_id': self.team_id, 'user_id': self.user_id, 'league_id': self.league_id, 'name': self.name,
                'created_on': self.created_on}
