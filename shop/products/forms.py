# from flask_wtf.file import FileAllowed, FileField, FileRequired
# from wtforms import IntegerField,StringField, BooleanField, TextAreaField, validators, Form,SubmitField

# class Addproducts(Form):
#     name = StringField('Name', [validators.data_required()])
#     price = IntegerField('Price', [validators.data_required()])
#     discount = IntegerField('Discount', default=0)
#     stock = IntegerField('Stock', [validators.data_required()])
#     description = TextAreaField('Description', [validators.data_required()])
#     colors = TextAreaField('Colors', [validators.data_required()])

#     image_1 = FileField('Image_1', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'])])
#     image_2 = FileField('Image_2', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'])])
#     image_3 = FileField('Image_3', validators=[FileRequired(), FileAllowed(['jpg','png','gif','jpeg'])])
#     submit = SubmitField('Add Product')
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CSRFForm(FlaskForm):
    pass

class Addproducts(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    discount = DecimalField('Discount', validators=[NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    colors = StringField('Colors', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_1 = FileField('Image 1')
    image_2 = FileField('Image 2')
    image_3 = FileField('Image 3')
    submit = SubmitField('Add Product')
