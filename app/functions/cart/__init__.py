from .use_model import Blueprint
from app.config import path
from app.functions.models.sql_connect import *

cart_blueprint = Blueprint("cart_blueprint", __name__, static_folder=path + "static",
                           template_folder=path + r"templates\cart", url_prefix='/cart')


from . import route
