from flask_wtf import FlaskForm
from wtforms import (
    DecimalField, StringField, FloatField, IntegerField, TextAreaField,
    SelectField, SelectMultipleField, SubmitField, DateField
)
from wtforms.validators import InputRequired, Length, NumberRange, Optional, DataRequired
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed, FileRequired

ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'webp']

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class BookForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(max=255)])
    price = DecimalField("Precio", validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField("Cantidad", validators=[DataRequired(), NumberRange(min=0)])
    release_date = DateField("Fecha de lanzamiento", format="%Y-%m-%d", validators=[Optional()])
    format = StringField("Formato", validators=[Optional(), Length(max=50)])
    editorial = StringField("Editorial", validators=[Optional(), Length(max=100)])
    author_name = StringField("Autor", validators=[DataRequired(), Length(max=100)])
    synopsis = TextAreaField("Sinopsis", validators=[Optional(), Length(max=2000)])
    genres = SelectMultipleField("Géneros", coerce=int, validators=[Optional()])
    image = FileField("Portada (JPG/PNG)", validators=[
        FileAllowed(tuple(ALLOWED_EXT), "Solo imágenes (png, jpg, jpeg, webp)")
    ])
    submit = SubmitField("Guardar")
