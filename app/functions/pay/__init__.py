from .use_model import Blueprint, redirect, request
from app.config import path
from app.functions.models.sql_connect import *

pay_blueprint = Blueprint("pay_blueprint", __name__, static_folder=path + "static",
                          template_folder=path + r"templates\pay", url_prefix='/pay')

from . import route
