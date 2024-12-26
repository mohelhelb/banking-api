
### IMPORTS ####################################################################

from datetime import datetime
from marshmallow import (
        fields,
        Schema as BaseSchema,
        validates,
        validates_schema,
        ValidationError)
from marshmallow.validate import Email, Length

from app.models import User
from app.utils.currency import ExchangeRate


### CUSTOM VALIDATION CLASSES ##################################################   

class Account:

    def __init__(self, exist=False):
        self._exist = exist

    def __call__(self, value):
        user = User.filter_users_by(email=value)
        if self._exist and not user:
            raise ValidationError("The email address provided doesn't exist.")
        if not self._exist and user:
            raise ValidationError("The email address provided already exists.")    


class EmptyString:

    def __init__(self, allow=True, message=None, status_code=400):
        self._allow = allow
        self._message = "This field cannot be empty." if not message else message
        self._status_code = status_code

    def __call__(self, value):
        if not isinstance(value, str):
            raise Exception(f"{type(self).__name__} validator is applied only to fields of type string.")
        if not self._allow and value.strip() == "":
            raise ValidationError({"status_code": self._status_code, "message": self._message})


class PositiveNumber:

    def __init__(self, message=None, status_code=400):
        self._message = "This field must be positive."
        self._status_code = status_code

    def __call__(self, value):
        if not isinstance(value, float):
            raise Exception(f"{type(self).__name__} validator is applied only to fields of type float.")
        if value <= 0:
            raise ValidationError({"status_code": self._status_code, "message": self._message})


### BASE SCHEMA ################################################################

class Schema(BaseSchema):

    def handle_error(self, err, data, **kwargs):
        """Generate custom validation error messages."""
        if err.messages:
            errors = {}
            for field_name in err.messages:
                for err_message in err.messages[field_name]:
                    try:
                        status_code = err_message.get("status_code")
                    except AttributeError:
                        status_code = 400
                    if status_code not in errors:
                        errors[status_code] = []
                    try:
                        errors[status_code].append({field_name: err_message["message"]})
                    except TypeError:
                        errors[status_code].append({field_name: err_message})
            raise ValidationError(errors)


### SCHEMAS: AUTHENTICATION ####################################################
                                                    
class RegisterSchema(Schema):                                    
    name = fields.String(
            required=True,
            validate=[EmptyString(allow=False), Length(max=128)]) 

    email = fields.String(
            required=True,
            validate=[
                EmptyString(allow=False),
                Length(max=128),
                Email(),
                Account(exist=False)]) 

    password = fields.String(
            required=True,
            validate=[EmptyString(allow=False), Length(max=128)])  

    balance = fields.Float(required=True)  


class LoginSchema(Schema): 
    email = fields.String(
            required=True,
            validate=[
                EmptyString(allow=False, message="Bad credentials.", status_code=401),
                Length(max=128),
                Email(),
                Account(exist=True)]) 

    password = fields.String(
            required=True,
            validate=[
                EmptyString(allow=False, message="Bad credentials.", status_code=401),
                Length(max=128)])   

    @validates_schema
    def validate_password(self, data, **kwargs):
        email = data.get("email")
        password = data.get("password")
        user = User.filter_users_by(email=email)
        if user and not user.verify_password(password=password):
            raise ValidationError({"password": [{"status_code": 401, "message": "Bad credentials."}]})  


### SCHEMAS: RECURRING EXPENSES ################################################   

class RecurringExpenseSchema(Schema):
    expense_name = fields.String(
            required=True,
            validate=[EmptyString(allow=False), Length(max=255)])

    amount = fields.Float(required=True, validate=[PositiveNumber()])

    frequency = fields.String(
            required=False,
            validate=[EmptyString(allow=False), Length(max=50)]) 

    start_date = fields.String(required=True)

    @validates("start_date")
    def validate_start_date(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Date format must be 'yyyy-mm-dd' (e.g. '2024-03-16').")    


### SCHEMAS: TRANSFERS #########################################################

class TransferSchema(Schema):
    source_currency = fields.String(
            required=True,
            validate=[EmptyString(allow=False)])

    target_currency = fields.String(
            required=True,
            validate=[EmptyString(allow=False)])

    amount = fields.Float(required=True, validate=[PositiveNumber()])  
    
    @validates_schema
    def validate_currency(self, data, **kwargs):
        exchange_rates = ExchangeRate()  
        source_currencies = exchange_rates.source_currencies
        target_currencies = exchange_rates.target_currencies 

        source_currency = data.get("source_currency")
        target_currency = data.get("target_currency")
                                                         
        if source_currency not in source_currencies:
            raise ValidationError({"source_currency": [{"status_code": 404, "message": "Non-supported currency."}]})  
        if target_currency not in target_currencies:
            raise ValidationError({"target_currency": [{"status_code": 404, "message": "Non-supported currency."}]})     


### SCHEMAS: ALERTS ############################################################

class AlertSchema(Schema):
    target_amount = fields.Float(required=True, validate=[PositiveNumber()])

    alert_threshold = fields.Float(required=True, validate=[PositiveNumber()])

    balance_drop_threshold = fields.Float(required=True, validate=[PositiveNumber()])


### SCHEMAS: TRANSACTIONS ######################################################

class TransactionSchema(Schema):
    amount = fields.Float(required=True, validate=[PositiveNumber()])

    category = fields.String(
            required=True,
            validate=[EmptyString(allow=False)])

    timestamp = fields.String(required=False)

    @validates("timestamp")
    def validate_timestamp(self, value): 
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValidationError("Date format must be 'yyyy-mm-ddThh:mm:ssZ' (e.g. '2024-03-16T17:34:41Z').")                                                                  
