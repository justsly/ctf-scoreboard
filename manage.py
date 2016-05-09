import sys
import os
import random
import string
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import url_for
from flask_script import Manager, Server
from leaderboard.app import create_app
from leaderboard.model import db, Member, Code

app = create_app()
manager = Manager(app)

manager.add_command("runserver", Server(
    use_debugger=False,
    use_reloader=False,
    host='0.0.0.0',
    port=1337))

CODE_LENGTH = 20

@manager.command
def drop():
    "Drops database tables"
    db.drop_all()

@manager.command
def create():
    "Creates database tables from sqlalchemy models"
    db.create_all()

@manager.command
def recreate():
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    drop()
    create()

@manager.command
def populate():
    names = ['max', 'matthias', 'jörg', 'holger', 'andreas', 'oliver', 'marco', 'rainer', 'dominik']

    for n in names:
        m = Member(n)
        db.session.add(m)

    #for n in range(1, 10):
    #    c = Code('SPO-' + random_str(CODE_LENGTH), n*100)
    #    db.session.add(c)

    db.session.commit()

@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)

def random_str(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

if __name__ == "__main__":
    manager.run()
