from flask import Blueprint, render_template, redirect, request
from app.config import path
from app.functions.models.sql_connect import *


orders_blueprint = Blueprint("orders_blueprint", __name__, static_folder=path + "static",
                             template_folder=path + r"templates\orders", url_prefix='/orders')

from . import route
