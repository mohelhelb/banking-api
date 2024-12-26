                                    
### IMPORTS ####################################################################

import jwt

from flask import current_app, jsonify, url_for
from flask_httpauth import HTTPTokenAuth
from jwt.exceptions import InvalidSignatureError

from app.models import User


### HELPER: AUTHENTICATION #####################################################

# Token-based authentication:
auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    try:
        payload = jwt.decode(token, key=current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except InvalidSignatureError:
        return None
    else:
        return User.filter_users_by(email=payload["email"])


@auth.error_handler
def auth_error(status=401):
    response_data = {
        "Error": "Access Denied",
        "Login": f"{url_for('auth.login', _external=True)}"}
    return jsonify(response_data), 401                
