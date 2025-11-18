from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import database, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm
from oauthlib.oauth2 import WebApplicationClient
import requests
from urllib.parse import urlencode, urlunparse

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
# Crear el blueprint
bp_auth = Blueprint('auth', __name__)
# -------------------- RUTA DE AUTENTICACIÓN (LOGIN/REGISTRO) --------------------
@bp_auth.route("/auth", methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    login_form = LoginForm(prefix='login')
    register_form = RegistrationForm(prefix='register')
    
    # Manejar login
    if login_form.validate_on_submit() and 'login-submit' in request.form:
        user = User.query.filter_by(email=login_form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            
            if user.is_admin:
                return redirect(url_for('admin.panel_admin'))
                
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Error de inicio de sesión. Por favor, verifica el email y la contraseña.', 'danger')
    
    # Manejar registro
    if register_form.validate_on_submit() and 'register-submit' in request.form:
        try:
            existing_user = User.query.filter_by(email=register_form.email.data).first()
            if existing_user:
                flash('Este email ya está registrado. Por favor usa otro.', 'warning')
            else:
                hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
                user = User(name=register_form.name.data, email=register_form.email.data, password_hash=hashed_password)
                database.session.add(user)
                database.session.commit()
                flash(f'¡Cuenta creada para {register_form.name.data}! Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('auth.auth'))
        except Exception as e:
            database.session.rollback()
            flash('Error al crear la cuenta.', 'danger')
    
    return render_template('auth.html', login_form=login_form, register_form=register_form)


# -------------------- AUTENTICACIÓN CON GOOGLE --------------------
@bp_auth.route("/login/google") 
def login_google():
    if current_user.is_authenticated:
        
        return redirect(url_for('main.index'))
    
    
    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("login/google", "callback/google"),
        
        scope=current_app.config['GOOGLE_SCOPE'], 
        prompt="select_account"
    )
    return redirect(request_uri)


@bp_auth.route("/callback/google")
def callback_google():
    
    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    
    code = request.args.get("code")
    
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET'])
    )

    client.parse_request_body_response(token_response.text)
    
    
    uri, headers, body = client.add_token(current_app.config['GOOGLE_USER_INFO_URL'])
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        google_id = userinfo_response.json()["id"]
        email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        name = userinfo_response.json()["name"]
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            
            user = User(name=name, email=email, password_hash='oauth_user') 
            database.session.add(user) 
            database.session.commit()
            flash('¡Cuenta de Google registrada con éxito!', 'success')
        
        login_user(user)
        
        return redirect(url_for('main.index'))
    else:
        flash("El email de Google no pudo ser verificado.", 'danger')
        
        return redirect(url_for('auth.auth'))
    
# -------------------- CIERRE DE SESIÓN --------------------

@bp_auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp_auth.route("/profile")
@login_required 
def profile():
    return render_template('profile.html', title='Perfil', user=current_user)