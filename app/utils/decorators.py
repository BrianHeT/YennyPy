from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Necesitas iniciar sesión como administrador.', 'warning')
            return redirect(url_for('auth.auth'))
        
        if not current_user.is_admin:
            flash('No tienes permisos de administrador para acceder a esta página.', 'danger')
            abort(403)  
        
        return f(*args, **kwargs)
    return decorated_function