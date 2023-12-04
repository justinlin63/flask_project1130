from flask import Blueprint
from app.config import path
from app.functions.models.sql_connect import *

redirect_blueprint = Blueprint("redirect_blueprint", __name__, static_folder=path + "static",
                               template_folder=path + r"templates\redirect", url_prefix='/redirect')

from . import route
