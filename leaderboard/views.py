import re
import operator

from flask import render_template, Blueprint, request, redirect, flash, abort
from flask_login import login_user, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt
from leaderboard.model import db, Member, Code, CodeRedeem, QuizQuestion, QuizAnswer

frontend = Blueprint('frontend', __name__)
bcrypt = Bcrypt()

HINT_BUY_PRICE = 40

@frontend.route('/')
def index():
    """ show leaderboard """
    members = Member.query.all()

    # sort by points
    members.sort(key=operator.methodcaller('get_points'))

    members = reversed(members)

    qlen = 0
    try:
        if not current_user.is_anonymous():
            qlen = len(get_available_questions(current_user))
    except:
        pass

    return render_template('index.html', leaderboard=members, qlen=qlen)

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

        # firstblood
        if CodeRedeem.query.filter_by(code_id=c.id).count() == 0:
            current_user.points_bonus += 20

        cr = CodeRedeem(c, m)
        db.session.add(cr)

        db.session.commit()

        flash('Congratz, points redeemed.')

        return redirect('/')

    return render_template('redeem.html')

@frontend.route('/buyhint', methods=['GET', 'POST'])
@login_required
def buy_hint():
    """ Buy hints """
    challenges = [
        {
            'name':'Secure Framework',
            'hint':'Benutzername : Passwort : UID : GID : Info : Heimatverzeichnis : Shell'
        },
        {
            'name':'Zero Impact Security',
            'hint':'In dieser Aufgabe steckt viel Herzblut drin ;-) http://i.imgur.com/NScbv1N.png'
        },
        {
            'name':'Catch me if you can',
            'hint':'ROT13'
        },
        {
            'name':'Simple Login',
            'hint':'http://lmgtfy.com/?q=sql+injection'
        },
        {
            'name':'Image Hub',
            'hint':'Imagemagick? Imagetragick!'
        },
        {
            'name':'20th Century Filereader',
            'hint':'We are legion, we are _anonymous. The _path_ is the true destination.'
        },
        {
            'name':'Tables of Facepalm',
            'hint':'Use the source, Luke!'
        },
        {
            'name':'H4x0r Chatwall',
            'hint':'d2luZG93LmxvY2F0aW9uIGlzdCBkZWluIGZyZXVuZAo='
        },
        {
            'name':'Pingcommander',
            'hint':'https://www.gnu.org/software/bash/manual/bashref.html#Lists'
        },
        {
            'name':'Blind Date',
            'hint':'Order by? Union? More than one less than seven.'
        }
    ]

    if request.method == 'POST':
        try:
            buy_index = int(request.form.get('buy', -1))
        except:
            return abort(403)

        if buy_index == -1 or buy_index < 0 or buy_index > (len(challenges)-1):
            return abort(403)

        if (current_user.get_points() - HINT_BUY_PRICE) < 0:
            return render_template('buy_hint.html', challenges=challenges, error='You have not enough points to buy a hint')

        current_user.points_handicap += HINT_BUY_PRICE
        db.session.add(current_user)
        db.session.commit()

        flash('Hint: %s' % challenges[buy_index]['hint'])

    return render_template('buy_hint.html', challenges=challenges)

@frontend.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    """ Show and save quiz questions """
    questions = get_available_questions(current_user)

    if request.method == 'POST':
        for val in request.form:
            ret = re.search('answer-question-([0-9]+)', val)
            if ret is None:
                continue

            question_id = ret.group(1)

            for q in questions:
                if q.id == int(question_id):
                    qa = QuizAnswer(q, current_user, request.form.get('answer-question-%s' % question_id))
                    db.session.add(qa)
                    db.session.commit()

        flash('Saved.')
        return redirect('/quiz')

    return render_template('quiz.html', questions=questions, questions_len=len(questions))

@frontend.route('/quiz/show', methods=['GET'])
@login_required
def show_quiz():
    """ Show questions and answers """
    answers = current_user.quiz_answers

    return render_template('quiz_show.html', answers=answers)

def get_available_questions(user, limit=None):

    if not limit:
        print(len(user.code_redeems))
        flag_count = len(user.code_redeems)
        limit = 10 + (flag_count * 10)

    # always ensure same order
    questions = QuizQuestion.query.order_by(QuizQuestion.id).limit(limit)

    # get answers for user
    answers = QuizAnswer.query.filter_by(member_id=user.id).all()

    # only get IDs of answered questions
    answers_ids = [answer.question_id for answer in answers]

    # filter out answered questions
    questions = [question for question in questions if not question.id in answers_ids]

    return questions

def get_quiz_points(user):
    answers = QuizAnswer.query.filter_by(member_id=user.id).all()

    points = 0

    for answer in answers:
        if answer.solution == answer.question.solution:
            points += 20

    return points

def get_flag_points(user):
    flags = CodeRedeem.query.filter_by(member_id=user.id).all()

    points = 0

    for flag in flags:
        points += flag.code.points

    return points
