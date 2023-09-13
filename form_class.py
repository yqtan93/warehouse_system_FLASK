from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired


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