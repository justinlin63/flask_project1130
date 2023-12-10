from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, g
from flask_login import login_user, login_required, logout_user, current_user
from app.config import *
from ..models.sql_connect import *
from ..models.user import *
from werkzeug.security import check_password_hash, generate_password_hash
from app.functions.models.useful_string import *
from flask_dance.contrib.google import make_google_blueprint, google
import os
from requests_oauthlib import OAuth2Session
