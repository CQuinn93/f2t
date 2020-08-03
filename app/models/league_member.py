from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class LeagueMember(db.Model):
    __table_args__ = {"schema": "app"}

    league_member_id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, server_default='NOW()')

    def __repr__(self):
        return (f"<LeagueMember {self.league_member_id}, {self.league_id}, {self.user_id}, {self.team_id},"
                f"{self.created_on}>")

    def to_dict(self):
        return {'league_member_id': self.league_member_id, 'league_id': self.league_id, 'user_id': self.user_id,
                'team_id': self.team_id, 'created_on': self.created_on}
