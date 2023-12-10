from flask import Blueprint, render_template, request, redirect, flash, jsonify
from random import randint
from time import time
from app.config import *
from app.functions.models.sql_connect import *
from app.functions.login.route import login_required, current_user
from werkzeug.security import check_password_hash
from app.functions.models.useful_string import *
from uuid import uuid4
import json
import requests
