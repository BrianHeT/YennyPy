import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# --- Instancias de extensiones (sin app todavía) ---

database = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

basedir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)

    # Configuración
    DB_URL = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
    
# --- Configuración de Google Auth ---
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID")
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get("GOOGLE_CLIENT_SECRET")
# Definimos el SCOPE y la URL de autorización de Google
    app.config['GOOGLE_SCOPE'] = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
# URL de API para obtener el perfil de usuario (People API)
    app.config['GOOGLE_USER_INFO_URL'] = 'https://www.googleapis.com/oauth2/v1/userinfo'
    # Inicializar extensiones
    database.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, database)

    # Configurar login
    login_manager.login_view = 'main.login'  # ⚠️ Cambio aquí
    login_manager.login_message_category = 'info'

    # Importar modelos
    from .models import User

    # Cargar usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app