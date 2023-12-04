from flask import Blueprint, render_template, request
from random import randint
from app.config import *
from app.functions.models.sql_connect import *
from app.functions.login.route import current_user,login_required
from app.functions.models.useful_string import *
