
### IMPORTS ####################################################################

import jwt
import statistics

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import current_app, render_template
from flask_mail import Message
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from typing import List     

from app import bcrypt, db, mail 


### MODELS #####################################################################

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    balance: Mapped[float] = mapped_column(nullable=False, default=0.0)   
    # Relationship: RecurringExpense
    recurring_expenses: Mapped[List["RecurringExpense"]] = relationship(
            back_populates="user",
            cascade="all, delete-orphan")  
    # Relationship: Alert
    alerts: Mapped[List["Alert"]] = relationship(
            back_populates="user",
            cascade="all, delete-orphan")  
    # Relationship: Transaction
    transactions: Mapped[List["Transaction"]] = relationship(
            back_populates="user",
            cascade="all, delete-orphan")  

    @property
    def password(self):
        pass

    @password.setter
    def password(self, value):
        self.hashed_password = bcrypt.generate_password_hash(value).decode('UTF-8') 

    def __repr__(self):
        return f"{type(self).__name__}(id='{self.id}', name='{self.name}')"

    def add(self):
        db.session.add(self)
        db.session.commit()   

    def _avg_spending(self):
        spendings = [transaction.amount for transaction in self.transactions]
        return statistics.mean(spendings) if spendings else 0  

    @classmethod
    def filter_users_by(cls, email=None):  
        if email:
            stmt = db.select(cls).filter(cls.email == email)
            return db.session.execute(stmt).scalar()  

    @staticmethod
    def _generate_following_months(num_months=12):
        dt_now = datetime.utcnow()
        return [dt_now + relativedelta(months=i) for i in range(1, num_months + 1)]  

    def generate_json(self):
        data = {}
        data["name"] = self.name
        data["email"] = self.email
        data["hashedPassword"] = self.hashed_password
        return data  

    def generate_jwt(self, expiration_days=7):
        data = {}
        exp = datetime.utcnow() + timedelta(days=expiration_days)
        data["token"] = jwt.encode(
                    payload={"email": self.email, "exp": exp},
                    key=current_app.config["SECRET_KEY"],
                    algorithm="HS256")
        return data    

    def notify(self, initial_balance=None, final_balance=None):
        if initial_balance and final_balance:
            balance_dropped_by = abs(final_balance - initial_balance)
            for alert in self.alerts:
                alert_balance_drop_threshold = alert.balance_drop_threshold
                if balance_dropped_by > alert_balance_drop_threshold:
                    self._send_email(alert_balance=alert_balance_drop_threshold)
                    break  

    def projection(self):
        balance = self.balance
        statements = []
        base = {(dt.year, dt.month): 0.00 for dt in self._generate_following_months()}
        for expense in self.recurring_expenses:
            for date in base:
                if date >= expense.due_date:
                    base[date] += expense.amount
        for date in base:
            statement = {}
            month = f"{str(date[0])}-{str(date[1]).zfill(2)}"
            recurring_expense = base[date]
            balance = round(balance - recurring_expense, 2)
            statement["month"] = month
            statement["recurring_expense"] = recurring_expense
            statement["expected_balance"] = balance
            statements.append(statement)
        return statements  

    def _send_email(self, alert_balance=None):
        msg = Message(
                subject="CaixaBank: Balance Drop Alert",
                recipients=[self.email],
                body=render_template(
                    "mail/balance_drop_alert.txt",
                    user_name=self.name,
                    alert_balance_drop_threshold=alert_balance))
        mail.send(msg)  

    def _standard_deviation(self, date=None, period=90):
        max_date = date
        min_date = date - relativedelta(days=period)
        transactions = self.transactions
        sample = (t.amount for t in transactions if t.timestamp >= min_date and t.timestamp < max_date)
        try:
            sd = statistics.stdev(sample)
        except statistics.StatisticsError:
            sd = 0
        return sd   

    def update(self, balance=None):
        if balance:
            self.balance = balance
            db.session.commit()  
                    
    def verify_password(self, password=None):
        if password:
            return bcrypt.check_password_hash(self.hashed_password, password) 


class RecurringExpense(db.Model):
    __tablename__ = "recurring_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float]
    frequency: Mapped[str] = mapped_column(String(50), nullable=False, default="monthly")
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    # Relationship: User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="recurring_expenses")

    @validates("start_date")
    def validate_start_date(self, _, value):
        """Transform the 'start_date' field into a 'datetime' object."""
        return datetime.strptime(value, "%Y-%m-%d")  

    @property
    def due_date(self):
        return self.start_date.year, self.start_date.month  

    def __repr__(self):
        return f"{type(self).__name__}(id='{self.id}', user_id='{self.user_id}')"      

    def add(self):
        db.session.add(self)
        db.session.commit() 

    def delete(self):
        db.session.delete(self)
        db.session.commit()  

    @classmethod
    def filter_expenses_by(cls, id=None, user=None):
        if id and user:
            stmt = db.select(cls).filter(cls.id == id, cls.user_id == user.id)
            return db.session.execute(stmt).scalar()

    def generate_json(self):
        data = {}
        data["id"] = self.id
        data["expense_name"] = self.expense_name
        data["amount"] = self.amount
        data["frequency"] = self.frequency
        data["start_date"] = self.start_date.strftime("%Y-%m-%d")
        return data  

    def update(self, expense_name=None, amount=None, frequency=None, start_date=None):
        if expense_name:
            self.expense_name = expense_name
        if amount:
            self.amount = amount
        if frequency:
            self.frequency = frequency
        if start_date:
            self.start_date = start_date  
        db.session.commit()  


class Alert(db.Model):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_amount: Mapped[float] = mapped_column(nullable=False, default=0.0)
    alert_threshold: Mapped[float] = mapped_column(nullable=False, default=0.0)
    balance_drop_threshold: Mapped[float] = mapped_column(nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    # Relationship: User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="alerts")

    def __repr__(self):
        return f"{type(self).__name__}(id='{self.id}', user_id='{self.user_id}')"  

    def add(self):
        db.session.add(self)
        db.session.commit()  

    def delete(self):
        db.session.delete(self)
        db.session.commit()  

    @classmethod
    def filter_alerts_by(cls, id=None, user=None):
        if id and user:
            stmt = db.select(cls).filter(cls.id == id, cls.user_id == user.id)
            return db.session.execute(stmt).scalar()  

    def generate_json(self, exclude_fields=None):
        data = {}
        # Populate the data dictionary
        data["id"] = self.id
        data["user_id"] = self.user_id
        data["target_amount"] = self.target_amount  
        data["alert_threshold"] = self.alert_threshold  
        data["balance_drop_threshold"] = self.balance_drop_threshold
        # Remove given fields from the data dictionary
        if exclude_fields:
            for field in exclude_fields:
                try:
                    _ = data.pop(field)
                except KeyError:
                    continue
        return data  


class Transaction(db.Model):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    fraud: Mapped[bool] = mapped_column(default=False)  
    # Relationship: User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="transactions")   

    @validates("timestamp")
    def validate_timestamp(self, _, value):
        """Transform the 'timestamp' field into a 'datetime' object."""
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")  

    def __repr__(self):
        return f"{type(self).__name__}(id='{self.id}', user_id='{self.user.id}')"  

    def add(self):
        db.session.add(self)
        db.session.commit()  

    def comply_with(self, fraud_rule=None):
        user = self.user
        final_timestamp = self.timestamp
        category = self.category

        # Fraud Detection Rule 1:
        if fraud_rule == 1:
            standard_deviation = user._standard_deviation(date=final_timestamp)  
            return True if self.amount > 3 * standard_deviation else False

        # Fraud Detection Rule 2:
        if fraud_rule == 2:
            initial_timestamp = final_timestamp - relativedelta(days=180)
            similar_transactions = []
            for transaction in type(self)._filter_transactions_by(category=category, user=user):
                if final_timestamp > transaction.timestamp and initial_timestamp <= transaction.timestamp:
                    similar_transactions.append(transaction)
            return True if not similar_transactions else False    

        # Fraud Detection Rule 3:
        if fraud_rule == 3:
            initial_timestamp = final_timestamp - relativedelta(minutes=5)
            recurrent_transactions = []
            recurrent_spendings = []
            for transaction in user.transactions:
                if final_timestamp > transaction.timestamp and initial_timestamp <= transaction.timestamp:
                    recurrent_transactions.append(transaction)
            for transaction in recurrent_transactions:
                recurrent_spendings.append(transaction.amount)
            return True if len(recurrent_transactions) > 3 and sum(recurrent_spendings) > user._avg_spending() else False      

    @classmethod
    def _filter_transactions_by(cls, category=None, user=None):
        if category and user:
            stmt = db.select(cls).filter(cls.category == category, cls.user_id == user.id)
            return db.session.execute(stmt).scalars() 

    def generate_json(self):
        data = {}
        data["id"] = self.id
        data["user_id"] = self.user_id
        data["amount"] = self.amount
        data["category"] = self.category
        data["timestamp"] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        data["fraud"] = self.fraud
        return data    

    def update(self, fraud=False):
        if fraud:
            self.fraud = fraud
            db.session.commit()                
