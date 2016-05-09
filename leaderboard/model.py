from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    points = db.Column(db.Integer)

    def __init__(self, name=None, points=0):
        self.name = name
        self.points = points

    def __repr__(self):
        return '<User %r, %r points>' % (self.name, self.points)

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    points = db.Column(db.Integer)

    def __init__(self, code=None, points=0):
        self.code = code
        self.points = points

    def __repr__(self):
        return '<Code %r, %r points>' % (self.code, self.points)

class CodeRedeem(db.Model):
    __tablename__ = 'code_redeem'

    id = db.Column(db.Integer, primary_key=True)

    code_id = db.Column(db.Integer, db.ForeignKey('code.id'))
    code = db.relationship('Code', backref=db.backref('codes', lazy='dynamic'))

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    member = db.relationship('Member', backref=db.backref('members', lazy='dynamic'))

    def __init__(self, code, member):
        self.code = code
        self.member = member
