from flask import render_template, Blueprint, request, redirect, flash
from leaderboard.model import db, Member, Code, CodeRedeem

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    """ show leaderboard """
    members = Member.query.order_by("points desc")

    return render_template('index.html', leaderboard=members)

@frontend.route('/redeem', methods=['GET', 'POST'])
def redeem():
    """ redeem points """
    members = Member.query.all()

    if request.method == 'POST':

        name = request.form.get('name', '')
        code = request.form.get('code', '')

        c = Code.query.filter(Code.code == code).first()

        if not c:
            return render_template('redeem.html', members=members, error='Invalid code')

        m = Member.query.filter(Member.name == name).first()
        if not m:
            return render_template('redeem.html', members=members, error='Invalid member')

        if CodeRedeem.query.filter(CodeRedeem.member_id == m.id).filter(CodeRedeem.code_id == c.id).first():
            return render_template('redeem.html', members=members, error='Code already redeemed for this member')

        m.points = Member.points + c.points

        cr = CodeRedeem(c, m)
        db.session.add(cr)

        db.session.commit()

        flash('Congratz, points redeemed.')

        return redirect('/')

    return render_template('redeem.html', members=members)
