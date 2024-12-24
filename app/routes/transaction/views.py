
### IMPORTS ####################################################################

from flask import jsonify, request
from marshmallow import ValidationError

from app.models import Transaction
from app.routes.transaction import bp
from app.utils.helpers.auth import auth
from app.utils.schemas import TransactionSchema      


### VIEWS ######################################################################

@bp.route("", methods=["POST"])
@auth.login_required
def add_transaction():
    request_data = request.get_json()
    schema = TransactionSchema()
    try:
        validated_data = schema.load(request_data)
    except ValidationError as err:
        if err.messages.get(400):
            response_data = err.messages[400]
            return jsonify(response_data), 400
    else:
        # Add the transaction to the database
        user = auth.current_user()
        transaction = Transaction(**validated_data, user=user)
        transaction.add()

        # Mark the transaction as fraud if it complies with at least one of the fraud detection rules
        if transaction.comply_with(fraud_rule=1) or transaction.comply_with(fraud_rule=2) or transaction.comply_with(fraud_rule=3):
            transaction.update(fraud=True) 

        # Notify the user if the user's balance drops by more that chosen threshold
        balance_before_transaction = user.balance
        balance_after_transaction = balance_before_transaction - transaction.amount
        user.notify(
                initial_balance=balance_before_transaction,
                final_balance=balance_after_transaction)

        # Update the user's balance
        user.update(balance=balance_after_transaction)
        response_data = {
                "msg": "Transaction added and evaluated for fraud.",
                "data": transaction.generate_json()}
        return jsonify(response_data), 201   
