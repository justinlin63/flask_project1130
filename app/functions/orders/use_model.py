from flask import Blueprint, render_template, redirect
from random import randint
from app.config import *
from app.functions.models.sql_connect import *
from app.functions.login.route import current_user,login_required
from app.functions.pay.route import generate_refund_bill