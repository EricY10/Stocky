from flask_login import UserMixin
from . import db  

# Existing User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    # Relationship to link User with UserStock
    stocks = db.relationship('UserStock', backref='user', lazy=True)

#  UserStock model
class UserStock(db.Model):
    __tablename__ = 'user_stocks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to the User table
    stock_symbol = db.Column(db.String(10), nullable=False)
    num_shares = db.Column(db.Integer, nullable=False)  
    purchase_price = db.Column(db.Float, nullable=False)  

    def __repr__(self):
        return f"<UserStock {self.stock_symbol} ({self.num_shares})>"  


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    num_shares = db.Column(db.Integer, nullable=False)  
    price_per_share = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.num_shares} shares of {self.stock_symbol} at {self.price_per_share}>"
