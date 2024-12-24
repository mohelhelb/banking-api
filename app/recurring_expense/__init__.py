from flask import Blueprint

bp = Blueprint('recurring_expense', __name__)

from app.recurring_expense import views  
