from flask import Blueprint, render_template, request, current_app, redirect
import calendar
from datetime import datetime
from sqlalchemy import and_

import api.external as external
from api.models.calendar import User, Plan

base_url = 'http://127.0.0.1:5000'  # Flask アプリケーションが通常起動するアドレス

# Blueprint の設定。calendar_router という名前で、このファイルが属するモジュール(__name__)に関連付けられる。
app = Blueprint('calendar_router', __name__)

# ルート('/')の設定。GETとPOSTメソッドを処理する。
@app.route('/', methods=["GET", "POST"])
def index():
    # POSTリクエストの場合の処理
    if request.method == 'POST':
        # データベースから最初のユーザーを取得
        user = external.db.session.query(User).first()
        # ユーザーが存在しない場合
        if user is None:
            # 新しい User オブジェクトを作成
            user = User()
            # アプリケーションコンテキスト内でデータベースに新しいユーザーを追加し、コミットする
            with current_app.app_context():
                external.db.session.add(user)
                external.db.session.commit()
        # GETリクエストの場合、またはユーザー作成後に月のカレンダーページへリダイレクト
        return redirect(base_url + '/month')

    # GETリクエストの場合はログイン画面を表示
    return render_template('login.html')

# ルート('/month')の設定。GETとPOSTメソッドを処理し、月ごとのカレンダーを表示する。
@app.route('/month', methods=["GET", "POST"])
def month():
    # データベースから最初のユーザーを取得
    user = external.db.session.query(User).first()
    # ユーザーの現在の年と月を取得
    year = user.current_year
    month = user.current_month

    # ユーザーの現在の年または月が設定されていない場合は、現在の年と月を設定
    if user.current_year is None or user.current_month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    # POSTリクエストの場合の処理
    if request.method == 'POST':
        # 'action' がフォームに含まれているか確認
        if 'action' in request.form:
            # 'last_month' アクションの場合、月を1つ減らす
            if request.form['action'] == 'last_month':
                month = month - 1
                # 月が1より小さくなった場合、前年の12月に設定
                if month < 1:
                    month = 12
                    year = year - 1
            # 'next_month' アクションの場合、月を1つ増やす
            elif request.form['action'] == 'next_month':
                month = month + 1
                # 月が12より大きくなった場合、翌年の1月に設定
                if month > 12:
                    month = 1
                    year = year + 1
            # ユーザーの現在の年と月を更新し、データベースにコミット
            user.current_year = year
            user.current_month = month
            external.db.session.commit()

    # calendar モジュールを使用して、指定された年月のカレンダーデータを取得
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    # 月ごとのカレンダーを表示するテンプレートをレンダリング
    return render_template('month_calendar.html', year=year, month=month, month_days=month_days)

# ルート('/week')の設定。GETとPOSTメソッドを処理し、週ごとのカレンダーと予定を表示する。
@app.route('/week', methods=["GET", "POST"])
def week():
    # データベースから最初のユーザーを取得
    user = external.db.session.query(User).first()
    # ユーザーの現在の年、月、週を取得
    year = user.current_year
    month = user.current_month
    week = user.current_week

    # ユーザーの現在の年または月が設定されていない場合は、現在の年と月を設定
    if user.current_year is None or user.current_month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    # calendar モジュールを使用して、指定された年月のカレンダーデータを取得
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    # POSTリクエストの場合の処理
    if request.method == 'POST':
        # 'action' がフォームに含まれているか確認
        if 'action' in request.form:
            # 'last_week' アクションの場合、現在の週を1つ減らす
            if request.form['action'] == 'last_week':
                if week > 0:
                    week = week - 1
            # 'next_week' アクションの場合、現在の週を1つ増やす
            elif request.form['action'] == 'next_week':
                if week < len(month_days) - 1:
                    week = week + 1
            # ユーザーの現在の週を更新し、データベースにコミット
            user.current_week = week
            external.db.session.commit()

    # 指定された週のデータを取得
    month_week = month_days[week]
    # データベースから、現在のユーザー、年、月、そして表示する週に含まれる日の予定を取得
    plans = external.db.session.query(Plan)\
        .filter(Plan.user_id == user.id)\
        .filter(Plan.current_year == user.current_year)\
        .filter(Plan.current_month == user.current_month)\
        .filter(and_(Plan.current_day >= month_week[0], Plan.current_day <= month_week[6]))
    # 週の各日の予定テキストを格納するリスト
    plan_texts = []
    # 週の各日について処理
    for day in month_week:
        plan_text = ""
        # 日が0の場合（その月の日ではない）、空の予定テキストを追加して次の日へ
        if day == 0:
            plan_texts.append(plan_text)
            continue
        # 取得した予定の中から、その日の予定を探してテキストに追加
        for plan in plans:
            if day == plan.current_day:
                plan_text = plan_text + plan.plan_text + "\n"
        # その日の予定テキストをリストに追加
        plan_texts.append(plan_text)

    # 週ごとのカレンダーと予定を表示するテンプレートをレンダリング
    return render_template('week_calendar.html', year=year, month=month, month_week=month_week, plan_texts=plan_texts)

# ルート('/plan')の設定。GETとPOSTメソッドを処理し、予定の入力フォームを表示、または予定を保存する。
@app.route('/plan', methods=["GET", "POST"])
def plan():
    # データベースから最初のユーザーを取得
    user = external.db.session.query(User).first()
    # ユーザーの現在の年と月を取得
    year = user.current_year
    month = user.current_month
    # フォームから選択された日を取得
    day_str = request.form['day']
    day = int(day_str)
    # POSTリクエストの場合の処理
    if request.method == 'POST':
        # 'plan' がフォームに含まれているか確認
        if 'plan' in request.form:
            # フォームから入力された予定テキストを取得
            plan_str = request.form['plan']
            # 新しい Plan オブジェクトを作成
            plan = Plan(
                user_id = user.id,
                current_year = year ,
                current_month = month,
                current_day = day,
                plan_text = plan_str
            )
            # ユーザーの plans リストに新しい予定を追加
            user.plans.append(plan)
            # データベースに変更をコミット
            external.db.session.commit()
            # 週ごとのカレンダーページへリダイレクト
            return redirect(base_url + '/week')

    # GETリクエストの場合は予定入力フォームを表示するテンプレートをレンダリング
    return render_template('input_plan.html', year=year, month=month, day=day)