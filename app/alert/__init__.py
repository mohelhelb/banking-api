from flask import Blueprint

bp = Blueprint('alert', __name__)

from app.routes.alert import views  
