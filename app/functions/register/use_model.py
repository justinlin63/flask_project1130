from flask import Blueprint, render_template, request,redirect
from app.config import *
from ..models.sql_connect import *
from werkzeug.security import generate_password_hash
