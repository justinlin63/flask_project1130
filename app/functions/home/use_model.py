from flask import Blueprint, render_template, request, redirect, session
from random import randint
from app.config import *
from app.functions.models.sql_connect import *
from app.functions.login.route import current_user, login_required
from app.functions.models.useful_string import *
import uuid
