from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
# Importamos la base de datos y los modelos
from app.models import User, Book, Author, Genre, database as db 
# ⚠️ Asegúrate de importar tu formulario (ej: from .forms import BookForm)
# from .forms import BookForm 

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Middleware de Verificación de Acceso de Administrador ---
def check_admin_access():
    # Verifica si el usuario está logueado Y tiene rol de administrador
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acceso denegado: Se requiere ser Administrador.', 'danger')
        # Asume que 'main.index' es el endpoint para tu página principal
        # Si usas Blueprints, esto debería ser 'main_bp.index'
        return redirect(url_for('main.index')) 
    return None

# 1. RUTA READ/DASHBOARD (Listado principal de libros y usuarios)
# La ruta final será: /admin/
@admin_bp.route('/')
@login_required
def admin_panel():
    if check_admin_access():
        return check_admin_access()
        
    users = User.query.all()
    books = Book.query.all()
    
    # Aquí puedes pasar el formulario para la sección de 'Agregar Libro'
    # add_book_form = BookForm()
    
    return render_template('admin_panel.html', 
                           users=users, 
                           books=books,
                           # form=add_book_form, 
                           title='Panel de Administración')


# 2. RUTA CREATE (Agregar Nuevo Libro)
# La ruta final será: /admin/books/add
@admin_bp.route("/books/add", methods=['GET', 'POST'])
@login_required
def add_book():
    if check_admin_access():
        return check_admin_access()
        
    form = BookForm() # Asume BookForm tiene campos para title, author_id, synopsis, price

    if form.validate_on_submit():
        # Lógica de creación del libro
        
        # ⚠️ Necesitarás obtener el objeto Author o el nombre del Autor si usas author_name
        
        new_book = Book(
            title=form.title.data,
            # RELACIÓN: Usamos el ID del autor que viene del formulario si usas FK
            author_id=form.author_id.data, 
            # Si solo guardas el nombre para mostrar (columna author_name):
            author_name=form.author_name.data, 
            synopsis=form.synopsis.data,
            price=form.price.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash(f'Libro "{new_book.title}" agregado exitosamente.', 'success')
        return redirect(url_for('admin.admin_panel'))

    # GET: Mostrar el formulario de subida
    return render_template('admin_add_book.html', title='Agregar Libro', form=form)


# 3. RUTA UPDATE (Editar detalles de un libro existente)
# La ruta final será: /admin/books/edit/123
@admin_bp.route("/books/edit/<int:book_id>", methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if check_admin_access():
        return check_admin_access()
        
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Libro no encontrado.', 'warning')
        return redirect(url_for('admin.admin_panel'))

    # Cargar datos existentes del libro en el formulario
    form = BookForm(obj=book) 

    if form.validate_on_submit():
        # Lógica de actualización
        book.title = form.title.data
        book.author_id = form.author_id.data
        book.author_name = form.author_name.data
        book.synopsis = form.synopsis.data
        book.price = form.price.data
        
        db.session.commit()
        flash(f'Libro "{book.title}" actualizado.', 'success')
        return redirect(url_for('admin.admin_panel'))

    # GET: Mostrar el formulario con los datos pre-llenados
    return render_template('admin_edit_book.html', title='Editar Libro', form=form, book=book)


# 4. RUTA DELETE (Eliminar Libro)
# La ruta final será: /admin/books/delete/123
@admin_bp.route("/books/delete/<int:book_id>", methods=['POST'])
@login_required
def delete_book(book_id):
    if check_admin_access():
        return check_admin_access()
        
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Libro no encontrado.', 'warning')
        return redirect(url_for('admin.admin_panel'))
    
    # Lógica de eliminación
    try:
        db.session.delete(book)
        db.session.commit()
        flash(f'Libro "{book.title}" eliminado permanentemente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el libro: {e}', 'danger')
    
    return redirect(url_for('admin.admin_panel'))