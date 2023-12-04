from flask import Blueprint
from app.config import path
from app.functions.models.sql_connect import *

home_blueprint = Blueprint("home_blueprint", __name__, static_folder=path + "static/product",
                           template_folder=path + r"templates\home")


from . import route
