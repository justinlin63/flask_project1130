from flask import Blueprint
from app.config import path
from app.functions.models.sql_connect import *

reset_password_blueprint = Blueprint("reset_password_blueprint", __name__, static_folder=path + "static",
                                     template_folder=path + r"templates\reset_password", url_prefix='/reset')

from . import route
