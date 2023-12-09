from flask import Flask
from os import urandom
from .functions import register_blueprints
from .config import *
from app.functions.models import sql_setting
from flask_login import LoginManager


def create_app():
    app = Flask(__name__, static_folder=path + 'static')
    app.config['SECRET_KEY'] = urandom(16)
    register_blueprints(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_blueprint.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.functions.models.user import get_user_by_id
        return get_user_by_id(user_id)
    return app
