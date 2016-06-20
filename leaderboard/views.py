from flask import render_template, Blueprint, request, redirect, flash, session
from flask_login import login_user, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt
from leaderboard.model import db, Member, Code, CodeRedeem

frontend = Blueprint('frontend', __name__)
bcrypt = Bcrypt()

@frontend.route('/')
def index():
    """ show leaderboard """
    members = Member.query.order_by("points desc")

    print(session)

    return render_template('index.html', leaderboard=members)

@frontend.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    member = Member.query.filter(Member.name == username).first()
    if member:
        if bcrypt.check_password_hash(member.password, password):
            member.authenticated = True
            login_user(member, remember=True)
            flash('Logged in.')
            return redirect('/')

    return redirect('/login')

@frontend.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect('/')

@frontend.route('/redeem', methods=['GET', 'POST'])
@login_required
def redeem():
    """ redeem points """

    if request.method == 'POST':

        code = request.form.get('code', '')

        c = Code.query.filter(Code.code == code).first()

        if not c:
            return render_template('redeem.html', error='Invalid code')

        m = current_user

        if CodeRedeem.query.filter(CodeRedeem.member_id == m.id).filter(CodeRedeem.code_id == c.id).first():
            return render_template('redeem.html', error='Code already redeemed')

        m.points = Member.points + c.points

        cr = CodeRedeem(c, m)
        db.session.add(cr)

        db.session.commit()

        flash('Congratz, points redeemed.')

        return redirect('/')

    return render_template('redeem.html')
