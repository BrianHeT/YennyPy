from flask_wtf import FlaskForm
from wtforms import (
    StringField, FloatField, IntegerField, TextAreaField,
    SelectField, SelectMultipleField, SubmitField, DateField
)
from wtforms.validators import InputRequired, Length, NumberRange, Optional
from wtforms.widgets import ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class BookForm(FlaskForm):
    title = StringField("Título", validators=[InputRequired(), Length(max=255)])
    price = FloatField("Precio", validators=[InputRequired(), NumberRange(min=0)])

    release_date = DateField("Fecha de lanzamiento", format="%Y-%m-%d", validators=[Optional()])

    format = StringField("Formato", validators=[Optional(), Length(max=50)])
    editorial = StringField("Editorial", validators=[Optional(), Length(max=100)])

    synopsis = TextAreaField("Sinopsis", validators=[Optional()])
    image = StringField("URL de imagen", validators=[Optional(), Length(max=255)])

    quantity = IntegerField("Stock", validators=[InputRequired(), NumberRange(min=0)])

    author_id = SelectField("Autor", coerce=int, validators=[Optional()])
    author_name = StringField("Nombre del autor (si no existe)", validators=[Optional(), Length(max=100)])

    genres = MultiCheckboxField("Géneros", coerce=int)

    submit = SubmitField("Guardar libro")
