from flask import Flask
import api.external as external
import os

def create_app():

    app = Flask(__name__)
    # USER='root'
    # PASSWORD='sqlpass'
    # HOST='localhost'
    # PORT = '3306'
    # DATABASE='calendar'
    # SQLALCHEMY_DATABASE_URI: str = 'mysql+pymysql://' + USER + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DATABASE + '?charset=utf8'
    # SQLALCHEMY_DATABASE_URI: str = 'mysql+pymysql://' + USER + ':' + PASSWORD + '@' + HOST + '/' + DATABASE + '?charset=utf8'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://docker:docker@mysql_db:3306/calendar'
    # DB設定を読み込む
    # app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
    DB_HOST = 'db'  # Docker Compose の場合は 'db' を使用することもできます
    DB_PORT = '3306'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}:{DB_PORT}/{MYSQL_DATABASE}'
    import api
    app.register_blueprint(api.calendar_app)

    return app

app = create_app()

external.init_db(app)

if __name__ == '__main__':
    app.run()
