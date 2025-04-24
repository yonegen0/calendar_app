from flask import Flask
import api.external as external

def create_app():

    app = Flask(__name__)
    USER='root'
    PASSWORD='sqlpass'
    HOST='localhost'
    # PORT = '3306'
    DATABASE='calendar'
    # SQLALCHEMY_DATABASE_URI: str = 'mysql+pymysql://' + USER + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DATABASE + '?charset=utf8'
    SQLALCHEMY_DATABASE_URI: str = 'mysql+pymysql://' + USER + ':' + PASSWORD + '@' + HOST + '/' + DATABASE + '?charset=utf8'

    # DB設定を読み込む
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    import api
    app.register_blueprint(api.calendar_app)

    return app

app = create_app()

external.init_db(app)

if __name__ == '__main__':
    app.run()
