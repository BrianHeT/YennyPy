from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


# -------------------- FORMULARIO DE REGISTRO --------------------

class RegistrationForm(FlaskForm):
    name = StringField('Nombre de Usuario',
                       validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo Electrónico',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    
    def validate_email(self, email):
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ese correo ya está registrado. Por favor, elige uno diferente.')

# -------------------- FORMULARIO DE LOGIN --------------------

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')  
    submit = SubmitField('Iniciar Sesión')
        