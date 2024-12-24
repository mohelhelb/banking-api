                                
### IMPORTS ####################################################################

from flask import jsonify, request
from marshmallow import ValidationError
                                         
from app.routes.transfer import bp
from app.utils.helpers.auth import auth
from app.utils.helpers.currency import ExchangeFee, ExchangeRate
from app.utils.schemas import TransferSchema    
              

### IMPORTS ####################################################################   

@bp.route('/fees')
@auth.login_required
def return_exchange_fee():
    request_data = {}
    request_data["source_currency"] = request.args.get("source_currency")
    request_data["target_currency"] = request.args.get("target_currency")
    schema = TransferSchema() 
    try:
        validated_data = schema.load(request_data, partial=("amount",))
    except ValidationError as err:  
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400  
        if err.messages.get(404):   
            response_data = err.messages[404] 
            return jsonify(response_data), 404
    else:
        exchange_fees = ExchangeFee()
        exchange_fee = exchange_fees.filter_by(
                source_currency=validated_data["source_currency"],
                target_currency=validated_data["target_currency"])
        response_data = {"exchangeFee": exchange_fee}
        return jsonify(response_data)    


@bp.route("/rates")
@auth.login_required
def return_exchange_rate():
    request_data = {}
    request_data["source_currency"] = request.args.get("source_currency")
    request_data["target_currency"] = request.args.get("target_currency")
    schema = TransferSchema()
    try:
        validated_data = schema.load(request_data, partial=("amount",))
    except ValidationError as err:  
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400  
        if err.messages.get(404):  
            response_data = err.messages[404] 
            return jsonify(response_data), 404
    else:
        exchange_rates = ExchangeRate()
        exchange_rate = exchange_rates.filter_by(
                source_currency=validated_data["source_currency"],
                target_currency=validated_data["target_currency"])
        response_data = {"exchangeRate": exchange_rate}
        return jsonify(response_data)    


@bp.route("/simulate", methods=["POST"])
@auth.login_required
def simulate():
    request_data = request.get_json() 
    schema = TransferSchema()
    try:
        validated_data = schema.load(request_data)
    except ValidationError as err:   
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400  
        if err.messages.get(404):  
            response_data = err.messages[404] 
            return jsonify(response_data), 404  
    else:                                                  
        source_currency = validated_data["source_currency"]  
        target_currency = validated_data["target_currency"]

        exchange_fees = ExchangeFee()
        exchange_fee = exchange_fees.filter_by(
                source_currency=source_currency,
                target_currency=target_currency)

        exchange_rates = ExchangeRate()
        exchange_rate = exchange_rates.filter_by(
                source_currency=source_currency,
                target_currency=target_currency)

        sender_amount = validated_data["amount"]
        recipient_amount = round(sender_amount * (1 - exchange_fee) * exchange_rate, 2)
        
        response_data = {"msg": f"Amount in target currency: {recipient_amount}."}
        return jsonify(response_data), 201
                                                                                 
