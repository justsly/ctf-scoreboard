from flask import Flask, request, Response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import HTTPException

from .model import db, Member, Code
from .views import frontend


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'ak3lfka39kalgk3992ksflsj4929rkgslo39502k'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaderboard.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ADMIN_CREDENTIALS'] = ('admin', 'foobar-metasploit-spo-1337')

    db.init_app(app)


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

    return app
