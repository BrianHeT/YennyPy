from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import database, bcrypt
from .models import User, Book
from .forms import RegistrationForm, LoginForm
import json
from oauthlib.oauth2 import WebApplicationClient
import requests
from urllib.parse import urlencode, urlunparse

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# Crear el blueprint
bp = Blueprint('main', __name__)

# -------------------- RUTAS PÚBLICAS --------------------

@bp.route("/")
@bp.route("/index")
def index():
    return render_template('index.html', title='Inicio')

@bp.route("/about")
def about():
    return render_template('about.html', title='Acerca de')

# -------------------- CATÁLOGO DE LIBROS --------------------
@bp.route("/library")
def library():
    all_books = Book.query.order_by(Book.title.asc()).all()
    return render_template('library.html', title='Biblioteca Completa', books=all_books)

# -------------------- DETALLE DEL LIBRO --------------------
@bp.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', 
                           title=book.title, 
                           book=book)

# -------------------- REGISTRO DE USUARIO --------------------
@bp.route("/register")
def register():
    return redirect(url_for('main.auth'))

@bp.route("/login")
def login():
    return redirect(url_for('main.auth'))


@bp.route("/auth", methods=['GET', 'POST'])
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
                return redirect(url_for('main.auth'))
        except Exception as e:
            database.session.rollback()
            flash('Error al crear la cuenta.', 'danger')
    
    return render_template('auth.html', login_form=login_form, register_form=register_form)


# -------------------- AUTENTICACIÓN CON GOOGLE --------------------
@bp.route("/login/google") 
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


@bp.route("/callback/google")
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
        
        return redirect(url_for('main.login'))
    
# -------------------- CIERRE DE SESIÓN --------------------

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# -------------------- RUTA PERFIL USUARIO --------------------

@bp.route("/profile")
@login_required 
def profile():
    return render_template('profile.html', title='Perfil', user=current_user)