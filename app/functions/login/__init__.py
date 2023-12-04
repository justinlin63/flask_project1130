from flask import Blueprint
from app.config import path
from ..models.sql_connect import *

login_blueprint = Blueprint("login_blueprint", __name__, static_folder=path + "static",
                            template_folder=path + r"templates\login")

from . import route
