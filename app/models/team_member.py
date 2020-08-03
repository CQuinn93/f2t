from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TeamMember(db.Model):
    __table_args__ = {"schema": "app"}

    team_member_id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False)
    player_id = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, server_default='NOW()')

    def __repr__(self):
        return f"<TeamMember {self.team_member_id}, {self.team_id}, {self.player_id}, {self.created_on}>"

    def to_dict(self):
        return {'team_member_id': self.team_id, 'team_id': self.team_id, 'player_id': self.player_id,
                'created_on': self.created_on}
