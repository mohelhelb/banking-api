### IMPORTS ####################################################################   

from flask import jsonify, request
from marshmallow import ValidationError
                           
from app.auth import bp   
from app.models import User
from app.schemas import LoginSchema, RegisterSchema, UpdateSchema
from app.utils.auth import auth


### VIEWS ######################################################################

@bp.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
    schema = RegisterSchema()
    try:
        validated_data = schema.load(request_data)
    except ValidationError as err:
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400
    else:
        user = User(**validated_data)
        user.add()
        response_data = user.generate_json()
        return jsonify(response_data), 201   


@bp.route("/login", methods=["POST"])
def login():
    request_data = request.get_json()
    schema = LoginSchema()
    try:
        validated_data = schema.load(request_data)
    except ValidationError as err:
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400
        if err.messages.get(401): 
            response_data = err.messages[401] 
            return jsonify(response_data), 401
    else:
        user = User.filter_users_by(email=validated_data["email"])  
        response_data = user.generate_jwt() 
        return jsonify(response_data)  


@bp.route("/update", methods=["POST"])
@auth.login_required
def update():
    request_data = request.get_json()
    schema = UpdateSchema()
    try:
        validated_data = schema.load(request_data)
    except ValidationError as err:
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400
        if err.messages.get(401): 
            response_data = err.messages[401] 
            return jsonify(response_data), 401
    else:
        print(validated_data)
        user = auth.current_user() 
        user.update(**validated_data)
        response_data = {"msg": "Account updated successfully."}
        return jsonify(response_data)  
    

@bp.route("/unregister")
@auth.login_required
def unregister():
    user = auth.current_user()
    user.delete()
    response_data = {"msg": "Account deleted successfully."}
    return jsonify(response_data)
