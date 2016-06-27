from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    points = db.Column(db.Integer)
    password = db.Column(db.String(60))

    def __init__(self, name=None, points=0):
        self.name = name
        self.points = points

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r, %r points>' % (self.name, self.points)

    def get_quiz_points(self):
        answers = self.qanswers

        points = 0

        for answer in answers:
            if answer.solution == answer.question.solution:
                points += 20

        return points

    def get_flag_points(self):
        flags = self.codesr

        points = 0

        for flag in flags:
            points += flag.code.points

        return points

    def get_points(self):
        return self.get_quiz_points() + self.get_flag_points()

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
    member = db.relationship('Member', backref=db.backref('codesr', lazy='dynamic'))

    def __init__(self, code, member):
        self.code = code
        self.member = member

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    answers = db.Column(db.PickleType)
    solution = db.Column(db.Integer)

    def __init__(self, text, answers, solution):
        self.text = text
        self.answers = answers
        self.solution = solution

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answer'

    solution = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), primary_key=True)
    question = db.relationship('QuizQuestion', backref=db.backref('qanswers', lazy='dynamic'))

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), primary_key=True)
    member = db.relationship('Member', backref=db.backref('qanswers', lazy='dynamic'))

    def __init__(self, question, member, solution):
        self.question = question
        self.member = member
        self.solution = solution

    def __repr__(self):
        return '<QuizAnswer %s, %s>' % (self.question.text, self.solution)
