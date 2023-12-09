from flask import Blueprint, render_template, request,redirect
from app.config import *
from app.functions.models.sql_connect import *
from app.functions.models.useful_string import *
from werkzeug.security import generate_password_hash
