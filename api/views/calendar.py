from flask import Blueprint, render_template, request, current_app, redirect
import calendar
from datetime import datetime
from sqlalchemy import and_

import api.external as external
from api.models.calendar import User, Plan

base_url = 'http://127.0.0.1:5000'  # Flask アプリケーションが通常起動するアドレス

# set route
app = Blueprint('calendar_router', __name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        user = external.db.session.query(User).first()
        if user is None:
            user = User()
            with current_app.app_context():
                external.db.session.add(user)
                external.db.session.commit()
        # GET リクエスト
        return redirect(base_url + '/month')

    return render_template('login.html')

@app.route('/month', methods=["GET", "POST"])
def month():
    user = external.db.session.query(User).first()
    year = user.current_year
    month = user.current_month

    if user.current_year is None or user.current_month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    if request.method == 'POST':
        if 'action' in request.form:
            if request.form['action'] == 'last_month':
                month = month - 1
                if month < 1:
                    month = 12
                    year = year - 1
            elif request.form['action'] == 'next_month':
                month = month + 1
                if month > 12:
                    month = 1
                    year = year + 1
            # with current_app.app_context():
            user.current_year = year
            user.current_month = month
            external.db.session.commit()
            

    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    return render_template('month_calendar.html', year=year, month=month, month_days=month_days)


@app.route('/week', methods=["GET", "POST"])
def week():
    user = external.db.session.query(User).first()
    year = user.current_year
    month = user.current_month
    week = user.current_week

    if user.current_year is None or user.current_month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    if request.method == 'POST':
        if 'action' in request.form:
            if request.form['action'] == 'last_week':
                if week > 0:
                    week = week - 1
            elif request.form['action'] == 'next_week':
                if week < len(month_days) - 1:
                    week = week + 1
            user.current_week = week
            external.db.session.commit()
    month_week = month_days[week]
    plans = external.db.session.query(Plan)\
        .filter(Plan.user_id == user.id)\
        .filter(Plan.current_year == user.current_year)\
        .filter(Plan.current_month == user.current_month)\
        .filter(and_(Plan.current_day >= month_week[0], Plan.current_day <= month_week[6]))
    plan_texts = []
    for day in month_week:
        plan_text = ""
        if day == 0:
            plan_texts.append(plan_text)
            continue
        for plan in plans:
            if day == plan.current_day:
                plan_text = plan_text + plan.plan_text + "\n"
        plan_texts.append(plan_text)

    return render_template('week_calendar.html', year=year, month=month, month_week=month_week, plan_texts=plan_texts)

@app.route('/plan', methods=["GET", "POST"])
def plan():
    user = external.db.session.query(User).first()
    year = user.current_year
    month = user.current_month
    day_str = request.form['day']
    day = int(day_str)
    if request.method == 'POST':
        if 'plan' in request.form:
            plan_str = request.form['plan']
            plan = Plan(
                user_id = user.id,
                current_year = year ,
                current_month = month,
                current_day = day,
                plan_text = plan_str
            )
            user.plans.append(plan)
            external.db.session.commit()
            return redirect(base_url + '/week')

    return render_template('input_plan.html', year=year, month=month, day=day)