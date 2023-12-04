from flask import Blueprint
from app.config import path
from app.functions.models.sql_connect import *

registers_blueprint = Blueprint("register_blueprint", __name__, static_folder=path + "static",
                                template_folder=path + r"templates\register")

from . import route
