from flask import Blueprint, render_template, request, session, redirect, abort
from werkzeug.security import generate_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.functions.models.sql_connect import *
from app.functions.models.useful_string import *
from app.config import ip
