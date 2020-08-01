from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean

from app import db, create_app
from app.controllers.goal_scored_controller import goal_scored_main
from app.models.goal_scored import GoalScored

app = create_app()
app.register_blueprint(goal_scored_main)

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
