import os
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from app.extensions import database, bcrypt
from .models import User

# --- Instancias de extensiones (sin app todavía) ---
login_manager = LoginManager()
migrate = Migrate()

basedir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    # Configuraciones de AWS S3
    app.config['AWS_ACCESS_KEY_ID'] = os.environ.get("AWS_ACCESS_KEY_ID")
    app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    app.config['AWS_S3_BUCKET'] = os.environ.get("AWS_S3_BUCKET") # 💡 Aquí se carga
    app.config['AWS_REGION'] = os.environ.get("AWS_REGION", 'us-east-1') 
    app.config['S3_UPLOAD_FOLDER'] = os.environ.get("S3_UPLOAD_FOLDER", "books")

    # Configuración de base de datos
    DB_URL = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'site.db')

    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://")

    # Solo agregar SSL si es PostgreSQL y NO es local
    if DB_URL.startswith("postgresql://") and "localhost" not in DB_URL and "127.0.0.1" not in DB_URL:
        app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL + "?sslmode=require"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

    # Estas configuraciones van FUERA del if/else
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
    login_manager.init_app(app)
    login_manager.login_view = 'auth.auth'
    login_manager.login_message = 'Por favor inicia sesión para continuar.'
    login_manager.login_message_category = 'info'
    
    # Error handlers personalizados
    @app.errorhandler(401)
    def unauthorized(error):
        """Usuario no autenticado intenta acceder a ruta protegida"""
        flash('Necesitas iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('auth.auth', next=request.url))
    
    @app.errorhandler(403)
    def forbidden(error):
        """Usuario autenticado pero sin permisos suficientes"""
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Página no encontrada"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Error interno del servidor"""
        database.session.rollback()
        return render_template('errors/500.html'), 500

    # Cargar usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprint
    from .blueprints import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    return app