from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# create an SQLAlchemy instance that interacts with the database and manage database operation
db = SQLAlchemy()

# Define database model
class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Amount %r>' % self.amount

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False, unique=True)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Product %r>' % self.product
    

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    history = db.Column(db.String(250), nullable=False)
    transaction_type = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<History %r>' % self.history