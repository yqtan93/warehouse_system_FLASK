
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask import Flask, render_template, redirect, url_for, flash
from flask_alembic import Alembic
from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired

# Create an instance of a Flask object
app = Flask(__name__)

# Contruct a path for SQLite database file
basedir = os.path.abspath(os.path.dirname(__file__))

# sets database connection URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir,'database.db')
# disables SQLAlchemy modification tracking features
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create secret key for form creation
app.config['SECRET_KEY'] = "temporary"

# Create a form class for purchase operation
class InventoryForm(FlaskForm):
    product_name = StringField("Product name", validators=[InputRequired()])
    price = DecimalField("Product price", validators=[InputRequired()])
    quantity = IntegerField("Quantity", validators=[InputRequired()])
    submit = SubmitField("Submit", validators=[InputRequired()])

# Create a form class for balance operation
class BalanceForm(FlaskForm):
    operation = SelectField("Operation type", choices=[('Debit', '+'), ('Credit', '-')])
    amount = IntegerField("Amount", validators=[InputRequired()])
    submit = SubmitField("Submit", validators=[InputRequired()])

# create an SQLAlchemy instance that interacts with the database and manage database operation
db = SQLAlchemy(app)

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


@app.route("/", methods=['GET', 'POST'])
def index():
    # retrieve all data from balance
    current_balance = db.session.query(Balance.amount).order_by(Balance.id.desc()).first()[0]
    # retrieve all data from inventory
    inventory = Inventory.query.all()
    return render_template("main.html", balance=current_balance, inventory=inventory)

@app.route("/purchase/<Action>", methods=['GET', 'POST'])
def purchase(Action):
    product_name, price, quantity =  None, None, None
    form = InventoryForm()
    # validate form input
    if form.validate_on_submit():
        
        product_name = form.product_name.data
        price = float(form.price.data)
        quantity = int(form.quantity.data)
        total_price = price * quantity

        current_balance = db.session.query(Balance.amount).order_by(Balance.id.desc()).first()[0]
        product = Inventory.query.filter_by(product_name=product_name).first()

        # Check if balance is sufficient
        if total_price < current_balance:
            # Check if product is already in inventory
            if product is None:
                # Add data onto inventory
                inventory = Inventory(product_name = product_name,
                                unit_price = price,
                                quantity = quantity)
                db.session.add(inventory)
                db.session.commit()

            else:
                # Update amount of existing product entry
                product.quantity += quantity
                db.session.add(product)
                db.session.commit()
            
            # Record history
            history = History(transaction_type = "Purchase",
                            history = f"{quantity} unit of {product_name} added. Total price: {total_price}")
            db.session.add(history)
            db.session.commit()

            # Update balance
            balance = Balance(amount = current_balance - total_price)
            db.session.add(balance)
            db.session.commit()

            # Show submission successful message
            flash("Purchase recorded successfully!")

        else:
            flash(f"Insufficient balance for purchase of {total_price}. Current balance: {current_balance} ")
    
        # Set value back to None
        # form.product_name.data = ''
        # form.price.data = ''
        # form.quantity.data = ''

        return redirect(url_for('purchase', Action=Action))
  
    return render_template("inventory_form.html", Action=Action, product_name=product_name, price=price, quantity=quantity, form=form)

@app.route("/sale/<Action>", methods=['GET', 'POST'])
def sale(Action):
    product_name, price, quantity =  None, None, None
    form = InventoryForm()
    # validate form input
    if form.validate_on_submit():
        product_name = form.product_name.data
        price = float(form.price.data)
        quantity = int(form.quantity.data)
        total_price = price * quantity

        current_balance = db.session.query(Balance.amount).order_by(Balance.id.desc()).first()[0]
        product = Inventory.query.filter_by(product_name=product_name).first()

        # Check if product is listed
        if product is not None:
            # Check if quantity sufficient
            if quantity <= product.quantity:
                # Update amount of existing product entry
                product.quantity -= quantity
                db.session.add(product)
                db.session.commit()
            
                # Record history
                history = History(transaction_type = "Sale",
                                history = f"{quantity} unit of {product_name} sold. Total income: {total_price}")
                db.session.add(history)
                db.session.commit()

                # Update balance
                balance = Balance(amount = current_balance + total_price)
                db.session.add(balance)
                db.session.commit()

                # Show submission successful message
                flash("Sale recorded successfully!")

            else:
                flash(f"Insufficient product quantity. Current quantity is {product.quantity}.")
        
        else:
            flash(f"Product {product_name} not in inventory.")
        

        # Set value back to None
        form.product_name.data = ''
        form.price.data = ''
        form.quantity.data = ''

        return redirect(url_for('sale', Action=Action))

    return render_template("inventory_form.html", Action=Action, product_name=product_name, price=price, quantity=quantity, form=form)

@app.route("/balance", methods=['GET', 'POST'])
def balance():
    amount =  None
    current_balance = db.session.query(Balance.amount).order_by(Balance.id.desc()).first()[0]
    form = BalanceForm()
    # validate form input
    if form.validate_on_submit():
        amount = float(form.amount.data)
        if form.operation.data == 'Debit':
            current_balance += amount
        elif form.operation.data == 'Credit':
            current_balance -= amount

        # Record history
        history = History(transaction_type = f"Balance - {form.operation.data}",
                        history = f"{form.operation.data} by {amount}. Current balance: {current_balance}")
        db.session.add(history)
        db.session.commit()

        # Update balance
        balance = Balance(amount = current_balance)
        db.session.add(balance)
        db.session.commit()

        flash("Balance updated successfully!")

        return redirect(url_for('balance'))


    return render_template("balance.html", amount=amount, form=form)

@app.route("/history", methods=['GET', 'POST'])
def history():
    # retrieve all data from history
    history = History.query.all()
    return render_template("history.html", history=history)

# Dynamic URL for purchase and sale pages
@app.route('/inventory/<Action>') 
def inventoryAction(Action):
    if Action == 'Sale':
        return redirect(url_for('sale', Action=Action))
    elif Action == 'Purchase':
        return redirect(url_for('purchase', Action=Action))
    
    
if __name__ == '__main__':
    app.run(debug=True)

# Use Alembic to manage database change
alembic = Alembic()
alembic.init_app(app)