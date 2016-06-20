import random
import string
import click

from flask import Flask, request, Response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import HTTPException

from .model import db, Member, Code
from .views import frontend

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ak3lfka39kalgk3992ksflsj4929rkgslo39502k'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaderboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_CREDENTIALS'] = ('admin', 'foobar-metasploit-spo-1337')

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)

bcrypt = Bcrypt()
bcrypt.init_app(app)

class ModelViewProtected(ModelView):
    def is_accessible(self):
        auth = request.authorization or request.environ.get('REMOTE_USER')
        if not auth or (auth.username, auth.password) != app.config['ADMIN_CREDENTIALS']:
            raise HTTPException('', Response(
                "Please log in.", 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            ))
        return True

admin = Admin(app, name='leaderboard', template_mode='bootstrap3')
admin.add_view(ModelViewProtected(Member, db.session))
admin.add_view(ModelViewProtected(Code, db.session))

app.register_blueprint(frontend)

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return Member.query.get(user_id)

@app.cli.command()
def initdb():
    "Creates database tables from sqlalchemy models"
    db.create_all()
@app.cli.command()
def dropdb():
    "Drops database tables"
    db.drop_all()

@app.cli.command()
def recreatedb():
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    db.drop_all()
    db.create_all()

@app.cli.command()
@click.argument('username')
def create_user(username):
    "Adds a member"
    m = Member(username)

    password_len = 10
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(password_len))
    m.password = bcrypt.generate_password_hash(password)

    db.session.add(m)
    db.session.commit()
    print('Added user %s:%s' % (username, password))

@app.cli.command()
@click.argument('username')
def remove_user(username):
    "Remove a member"
    Member.query.filter_by(name=username).delete()
    db.session.commit()
    print('Removed user ', username)
