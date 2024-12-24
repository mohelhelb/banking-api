
### IMPORTS ####################################################################

from flask import jsonify, request
from marshmallow import ValidationError

from app.models import Alert
from app.routes.alert import bp
from app.utils.auth import auth
from app.utils.schemas import AlertSchema     


### VIEWS ######################################################################  

@bp.route("/amount_reached", methods=["POST"])
@auth.login_required
def set_alert():
    request_data = request.get_json()
    schema = AlertSchema()
    exclude_fields = ("balance_drop_threshold",)
    try:
        validated_data = schema.load(request_data, partial=exclude_fields)
    except ValidationError as err: 
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400 
    else:
        user = auth.current_user()
        alert = Alert(**validated_data, user=user)
        alert.add()
        response_data = {
                "msg": "Correctly added savings alert!",
                "data": alert.generate_json(exclude_fields=exclude_fields)}
        return jsonify(response_data), 201    


@bp.route("/balance_drop", methods=["POST"])
@auth.login_required
def set_balance_drop():
    request_data = request.get_json()
    schema = AlertSchema()
    exclude_fields = ("target_amount", "alert_threshold")
    try:
        validated_data = schema.load(request_data, partial=exclude_fields)
    except ValidationError as err:  
        if err.messages.get(400):
            response_data = err.messages.get(400)
            return jsonify(response_data), 400  
    else:
        user = auth.current_user()
        alert = Alert(**validated_data, user=user)
        alert.add()   
        response_data = {
                "msg": "Correctly added balance drop alert!",
                "data": alert.generate_json(exclude_fields=exclude_fields)}
        return jsonify(response_data), 201      


@bp.route("/delete/<int:alert_id>", methods=["POST"])
@auth.login_required
def delete_alert(alert_id):
    user = auth.current_user()
    alert = Alert.filter_alerts_by(id=alert_id, user=user)
    if alert:
        alert.delete()
        response_data = {"msg": "Alert deleted successfully."}
        return jsonify(response_data)
    response_data = {"msg": "Alert not found."}
    return jsonify(response_data), 404   


@bp.route("/list")
@auth.login_required
def alert_list():
    user = auth.current_user()
    response_data = {"data": [alert.generate_json() for alert in user.alerts]}
    return jsonify(response_data) 
