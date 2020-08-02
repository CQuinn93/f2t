from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean

from app import create_app
from app.controllers.goal_scored_controller import goal_scored_main
from app.controllers.league_controller import league_main
from app.controllers.player_controller import player_main
from app.models.goal_scored import GoalScored

app = create_app()
app.register_blueprint(goal_scored_main, url_prefix='/goal_scored')
app.register_blueprint(league_main, url_prefix='/league')
app.register_blueprint(player_main, url_prefix='/player')

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """
    return dict(app=app, GoalScored=GoalScored)


if __name__ == "__main__":
    manager.run()
