from flask_login import UserMixin
from .sql_connect import *
from app.functions.models.useful_string import *


class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role


def get_user_by_id(user_id):
    username = sql_search('users', 'username', 'id', user_id)
    role = sql_search(ufstr.users(), ufstr.role(), ufstr.id(), user_id)
    return User(user_id, username, role)
