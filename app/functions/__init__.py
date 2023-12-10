from .home import home_blueprint
from .cart import cart_blueprint
from .login import login_blueprint
from .register import registers_blueprint
from .pay import pay_blueprint
from .orders import orders_blueprint
from .admin import admin_blueprint
from .reset_password import reset_password_blueprint
from .redirect import redirect_blueprint
from .login.route import google_blueprint
from flask import Flask

route_list = [home_blueprint, cart_blueprint, login_blueprint, registers_blueprint, pay_blueprint, orders_blueprint,
              admin_blueprint, reset_password_blueprint, redirect_blueprint]


def register_blueprints(app):
    for i in range(len(route_list)):
        app.register_blueprint(route_list[i])
    app.register_blueprint(google_blueprint, url_prefix='/login')
