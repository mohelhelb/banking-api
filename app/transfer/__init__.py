from flask import Blueprint

bp = Blueprint('transfer', __name__)

from app.routes.transfer import views  
