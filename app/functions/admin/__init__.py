from app.functions.admin.use_model import Blueprint
from app.config import path
from app.functions.models.sql_connect import *

admin_blueprint = Blueprint("admin_blueprint", __name__, static_folder=path + "static",
                            template_folder=path + r"templates\admin", url_prefix='/admin')

from . import route
