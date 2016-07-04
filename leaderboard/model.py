from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))

    quiz_answers = db.relationship('QuizAnswer', back_populates='member')
    code_redeems = db.relationship('CodeRedeem', back_populates='member')

    points_handicap = db.Column(db.Integer, default=0)
    points_bonus = db.Column(db.Integer, default=0)

    def __init__(self, name=None):
        self.name = name

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r, %r points>' % (self.name, self.get_points())

    def get_quiz_points(self):
        answers = self.quiz_answers

        points = 0

        for answer in answers:
            if answer.solution == answer.question.solution:
                points += 20

        return points

    def get_flag_points(self):
        flags = self.code_redeems

        points = 0

        for flag in flags:
            points += flag.code.points

        return points

    def get_firstbloods(self):
        return self.points_bonus // 20

    def get_points(self):
        return self.get_quiz_points() + self.get_flag_points() +self.points_bonus - self.points_handicap

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(56), unique=True)
    points = db.Column(db.Integer)

    code_redeems = db.relationship('CodeRedeem', back_populates='code', cascade='all, delete-orphan')

    def __init__(self, code=None, points=0):
        self.code = code
        self.points = points

    def __repr__(self):
        return '<Code %r, %r points>' % (self.code, self.points)

class CodeRedeem(db.Model):
    __tablename__ = 'code_redeem'

    id = db.Column(db.Integer, primary_key=True)

    code_id = db.Column(db.Integer, db.ForeignKey('code.id'))
    code = db.relationship('Code', back_populates='code_redeems')

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    member = db.relationship('Member', back_populates='code_redeems')

    def __init__(self, code, member):
        self.code = code
        self.member = member

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    answers = db.Column(db.PickleType)
    solution = db.Column(db.Integer)

    quiz_answers = db.relationship('QuizAnswer', back_populates='question', cascade='all, delete-orphan')

    def __init__(self, text, answers, solution):
        self.text = text
        self.answers = answers
        self.solution = solution

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answer'

    solution = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), primary_key=True)
    question = db.relationship('QuizQuestion', back_populates='quiz_answers')

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), primary_key=True)
    member = db.relationship('Member', back_populates='quiz_answers')

    def __init__(self, question, member, solution):
        self.question = question
        self.member = member
        self.solution = solution

    def __repr__(self):
        return '<QuizAnswer %s, %s>' % (self.question.text, self.solution)
