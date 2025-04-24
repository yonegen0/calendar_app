from api.external import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {
        'comment': 'ユーザー情報'
    }
    id = db.Column(db.Integer, primary_key=True)
    current_year = db.Column(db.Integer, default=datetime.now().year)
    current_month = db.Column(db.Integer, default=datetime.now().month)
    current_week = db.Column(db.Integer, default=0)
    plans = db.relationship('Plan', backref='calendar', cascade="all, delete-orphan", lazy=True, uselist=True, foreign_keys='Plan.user_id')

class Plan(db.Model):
    __tablename__ = 'plans'
    __table_args__ = {
        'comment': '予定'
    }
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # 明示的な外部キー、nullable=False
    current_year = db.Column(db.Integer, nullable=False)
    current_month = db.Column(db.Integer, nullable=False)
    current_day = db.Column(db.Integer, nullable=False)
    plan_text = db.Column(db.String(255), nullable=False)
    