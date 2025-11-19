from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
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
        
        
class ProfileUpdateForm(FlaskForm):
    name = StringField('Nombre',
                       validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    current_password = PasswordField('Contraseña Actual',
                                     validators=[Optional()])

    new_password = PasswordField('Nueva Contraseña',
                                 validators=[Optional(), Length(min=8)])
    confirm_new_password = PasswordField('Confirmar Nueva Contraseña',
                                         validators=[Optional(), EqualTo('new_password', message='Las contraseñas no coinciden.')])
    
    submit = SubmitField('Guardar Cambios')

    def validate_email(self, email):
        with app.app_context():
            # Buscar otro usuario con este email
            user = User.query.filter_by(email=email.data).first()
            if user and user.id != current_user.id:
                raise ValidationError('Ese correo ya está en uso por otra cuenta.')

    def validate_current_password(self, current_password):
        if self.new_password.data or self.confirm_new_password.data:
            if not current_password.data:
                raise ValidationError('Debes ingresar la Contraseña Actual para realizar el cambio.')
            
            if not bcrypt.check_password_hash(current_user.password_hash, current_password.data):
                raise ValidationError('La Contraseña Actual es incorrecta.')

