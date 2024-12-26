### IMPORTS ####################################################################

from flask import jsonify, request
from marshmallow import ValidationError

from app.models import RecurringExpense
from app.recurring_expense import bp 
from app.schemas import RecurringExpenseSchema  
from app.utils.auth import auth


### VIEWS ######################################################################

@bp.route("", methods=["GET", "POST"])
@auth.login_required
def create_recurring_expense():
    user = auth.current_user()
    if request.method == "GET":  
        response_data = [expense.generate_json() for expense in user.recurring_expenses]
        return jsonify(response_data) 
    if request.method == "POST":
        request_data = request.get_json()
        schema = RecurringExpenseSchema()
        try:
            validated_data = schema.load(request_data)
        except ValidationError as err:
            if err.messages.get(400):
                response_data = err.messages[400]
                return jsonify(response_data), 400
        else:
            recurring_expense = RecurringExpense(**validated_data, user=user)
            recurring_expense.add()
            response_data = {
                    "msg": "Recurring expense added successfully.",
                    "data": recurring_expense.generate_json()}
            return jsonify(response_data), 201 


@bp.route("/<int:expense_id>", methods=["DELETE", "PUT"])
@auth.login_required
def update_recurring_expense(expense_id):
    user = auth.current_user()
    recurring_expense = RecurringExpense.filter_expenses_by(id=expense_id, user=user)  
    if recurring_expense:
        if request.method == "DELETE":
            recurring_expense.delete()
            response_data = {"msg": "Recurring expense deleted successfully."}
            return jsonify(response_data)
        if request.method == "PUT":
            request_data = request.get_json()
            schema = RecurringExpenseSchema()
            try:
                validated_data = schema.load(request_data)
            except ValidationError as err:
                if err.messages.get(400):
                    response_data = err.messages[400]
                    return jsonify(response_data), 400 
            else:
                recurring_expense.update(**validated_data)  
                response_data = {
                        "msg": "Recurring expense updated successfully.",
                        "data": recurring_expense.generate_json()}  
                return jsonify(response_data)
    response_data = {"msg": "Recurring expense not found."}
    return jsonify(response_data), 404 


@bp.route('/projection')
@auth.login_required
def projection():
    user = auth.current_user()
    response_data = user.projection() 
    return jsonify(response_data)       
