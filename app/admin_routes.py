from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Book
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
@admin_bp.route('/')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Acceso denegado: No tienes permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    books = Book.query.all()
    
    return render_template('admin_panel.html', users=users, books=books)