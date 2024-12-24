from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy


# Instantiate extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()

def create_app(config_obj=None):
    # Create and configure the application
    app = Flask(__name__)
    app.config.from_object(config_obj)
    
    # Bind the extensions to the application
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Register the blueprints
    from app.routes import alert, auth, recurring_expense, transaction, transfer      
    app.register_blueprint(auth.bp, url_prefix="/api/auth")                      
    app.register_blueprint(recurring_expense.bp, url_prefix="/api/recurring-expenses")  
    app.register_blueprint(transfer.bp, url_prefix="/api/transfers")     
    app.register_blueprint(alert.bp, url_prefix="/api/alerts")    
    app.register_blueprint(transaction.bp, url_prefix="/api/transactions")

    return app
