from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import database, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm
from oauthlib.oauth2 import WebApplicationClient
import requests
from urllib.parse import urlencode, urlunparse
from datetime import datetime


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
                return redirect(url_for('admin.admin_panel'))
                
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
    
    try:
        client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
        
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash('Error de configuración de Google OAuth.', 'danger')
            return redirect(url_for('main.auth'))
        
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # ✅ Generar redirect_uri con HTTPS
        redirect_uri = url_for('auth.callback_google', _external=True, _scheme='https')
        
        current_app.logger.info(f"🔍 LOGIN - Redirect URI: {redirect_uri}")
        current_app.logger.info(f"🔍 LOGIN - Client ID: {current_app.config['GOOGLE_CLIENT_ID'][:20]}...")
        
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=current_app.config['GOOGLE_SCOPE'], 
            prompt="select_account"
        )
        
        return redirect(request_uri)
        
    except Exception as e:
        current_app.logger.error(f"❌ Error en login_google: {str(e)}", exc_info=True)
        flash('Error al iniciar el proceso de login con Google.', 'danger')
        return redirect(url_for('main.auth'))


@bp_auth.route("/callback/google")
def callback_google():
    try:
        # ✅ Verificar que se recibió el código
        code = request.args.get("code")
        if not code:
            current_app.logger.error("❌ No se recibió código de Google")
            flash('Error: No se recibió código de autorización.', 'danger')
            return redirect(url_for('main.auth'))
        
        current_app.logger.info(f"✅ Código recibido: {code[:20]}...")
        
        # ✅ Obtener configuración de Google
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            current_app.logger.error("❌ No se pudo obtener configuración de Google")
            flash('Error de configuración de Google.', 'danger')
            return redirect(url_for('main.auth'))
        
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
        
        # ✅ IMPORTANTE: usar HTTPS en producción
        redirect_url = url_for('auth.callback_google', _external=True, _scheme='https')
        authorization_response = request.url.replace('http://', 'https://')  # Forzar HTTPS
        
        current_app.logger.info(f"🔍 Redirect URL: {redirect_url}")
        current_app.logger.info(f"🔍 Authorization response: {authorization_response}")
        
        # Preparar petición del token
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=authorization_response,
            redirect_url=redirect_url,
            code=code
        )
        
        # Solicitar token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET'])
        )
        
        # ✅ Verificar que la respuesta del token sea exitosa
        if not token_response.ok:
            current_app.logger.error(f"❌ Error obteniendo token: {token_response.status_code} - {token_response.text}")
            flash('Error al obtener token de Google.', 'danger')
            return redirect(url_for('main.auth'))
        
        current_app.logger.info(f"✅ Token obtenido exitosamente")
        
        # Parsear respuesta del token
        client.parse_request_body_response(token_response.text)
        
        # Obtener información del usuario
        uri, headers, body = client.add_token(current_app.config['GOOGLE_USER_INFO_URL'])
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        # ✅ Verificar que la respuesta de userinfo sea exitosa
        if not userinfo_response.ok:
            current_app.logger.error(f"❌ Error obteniendo info de usuario: {userinfo_response.status_code}")
            flash('Error al obtener información del usuario.', 'danger')
            return redirect(url_for('main.auth'))
        
        userinfo = userinfo_response.json()
        current_app.logger.info(f"✅ Userinfo obtenido: {userinfo.get('email')}")
        
        # Verificar email
        if not userinfo.get("email_verified"):
            current_app.logger.warning(f"⚠️ Email no verificado: {userinfo.get('email')}")
            flash("El email de Google no pudo ser verificado.", 'danger')
            return redirect(url_for('main.auth'))
        
        # Extraer datos del usuario
        email = userinfo["email"]
        name = userinfo.get("name", email.split('@')[0])
        picture = userinfo.get("picture")
        
        current_app.logger.info(f"🔍 Buscando usuario con email: {email}")
        
        # Buscar o crear usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            current_app.logger.info(f"📝 Creando nuevo usuario: {email}")
            try:
                user = User(
                    name=name, 
                    email=email, 
                    password_hash='oauth_user',
                    email_verified_at=datetime.utcnow()
                )
                database.session.add(user)
                database.session.commit()
                
                current_app.logger.info(f"✅ Usuario creado exitosamente: {email}")
                flash(f'¡Bienvenido {name}! Tu cuenta ha sido creada.', 'success')
                
            except Exception as e:
                database.session.rollback()
                current_app.logger.error(f"❌ Error al crear usuario: {str(e)}")
                flash('Error al crear tu cuenta. Por favor, intenta nuevamente.', 'danger')
                return redirect(url_for('auth.auth'))
        else:
            current_app.logger.info(f"✅ Usuario existente encontrado: {email}")
            flash(f'¡Bienvenido de nuevo {name}!', 'success')
        
        # Loguear usuario
        login_user(user)
        current_app.logger.info(f"✅ Usuario logueado: {email}")
        
        return redirect(url_for('main.index'))
        
    except Exception as e:
        current_app.logger.error(f"❌ Error inesperado en callback: {str(e)}", exc_info=True)
        flash('Error al iniciar sesión con Google. Por favor, intenta nuevamente.', 'danger')
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