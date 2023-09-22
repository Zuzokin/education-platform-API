from flask import Flask

app = Flask(__name__)

USERS = {}  # dict for objects of type User with keys as ids
EXPRS = {}  # dict for objects of type Expr with keys as ids

from app import views
from app import models
