from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import database
from app.models import Book, Genre, Author
from app.bookforms import BookForm
from app.utils.s3 import upload_fileobj_to_s3, generate_presigned_url_for_key, delete_s3_key, get_s3_client 
from app.utils.decorators import admin_required 
from werkzeug.utils import secure_filename

bp_books = Blueprint("books", __name__, url_prefix="/books")

# ---- LISTADO PÚBLICO ----
@bp_books.route("/biblioteca")
def list_books():
    books = Book.query.all()
    
    books_with_images = [
        (book, book.image)
        for book in books
    ]
    
    return render_template("books/biblioteca.html", books=books_with_images)

# ---- DETALLE PÚBLICO ----
@bp_books.route("/<int:book_id>")
def details(book_id):
    s3_config = {
        'BUCKET': current_app.config.get('AWS_S3_BUCKET'),
        'REGION': current_app.config.get('AWS_REGION'),
        'BASE_URL': f"https://{current_app.config.get('AWS_S3_BUCKET')}.s3.{current_app.config.get('AWS_REGION')}.amazonaws.com/"
    }
    book = Book.query.get_or_404(book_id)

    image_url = None
    if book.image:
        image_url = generate_presigned_url_for_key(book.image)
    return render_template("books/details_book.html", book=book, image_url=image_url, s3_config=s3_config)

# ---- CREAR LIBRO (ADMIN) ----
@bp_books.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_book():
    form = BookForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]

    if form.validate_on_submit():
        # Validar que se subió una imagen
        f = request.files.get("image")
        if not f or f.filename == "":
            flash("La imagen de portada es obligatoria.", "danger")
            return render_template("books/create_book.html", form=form)
        
        # Subir imagen a S3
        filename = secure_filename(f.filename)
        try:
            s3_url = upload_fileobj_to_s3(f, filename)  # Retorna URL completa
    
            if not s3_url:
                flash("Error al subir la imagen a S3. Intentá nuevamente.", "danger")
                return render_template("books/create_book.html", form=form)
        
        except Exception as e:
            current_app.logger.error("S3 upload failed: %s", e)
            flash("Error al subir la imagen. Intentá nuevamente.", "danger")
            return render_template("books/create_book.html", form=form)

        # Crear el libro
        book = Book(
            title=form.title.data,
            price=float(form.price.data),
            quantity=form.quantity.data,
            release_date=form.release_date.data,
            format=form.format.data,
            editorial=form.editorial.data,
            synopsis=form.synopsis.data,
            image=s3_url,
            author_name=form.author_name.data
        )
        
        # Agregar géneros si fueron seleccionados
        if form.genres.data:
            book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()

        database.session.add(book)
        database.session.commit()
        
        flash("Libro creado correctamente.", "success")
        return redirect(url_for("books.list_books"))  

    return render_template("books/create_book.html", form=form)

# ---- EDITAR LIBRO (ADMIN) ----
@bp_books.route("/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]

    if form.validate_on_submit():
        f = request.files.get("image")
        if f and f.filename:
            filename = secure_filename(f.filename)
            try:
                new_key = upload_fileobj_to_s3(f, filename)

                if book.image:
                    try:
                        delete_s3_key(book.image)
                    except Exception:
                        current_app.logger.warning("Failed to delete old S3 key %s", book.image)
                book.image = new_key
            except Exception as e:
                current_app.logger.error("S3 upload failed: %s", e)
                flash("Error al subir la nueva imagen.", "danger")
                return render_template("books/edit_book.html", form=form, book=book)

        book.title = form.title.data
        book.price = float(form.price.data)
        book.quantity = form.quantity.data
        book.release_date = form.release_date.data
        book.format = form.format.data
        book.editorial = form.editorial.data
        book.synopsis = form.synopsis.data
        book.author_name = form.author_name.data
        if form.genres.data is not None:
            book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()

        database.session.commit()
        flash("Libro actualizado.", "success")
        return redirect(url_for("books.details_book", book_id=book.id))

    if request.method == "GET":
        form.genres.data = [g.id for g in book.genres]

    return render_template("books/edit_book.html", form=form, book=book)

# ---- ELIMINAR LIBRO (ADMIN) ----
@bp_books.route("/<int:book_id>/delete", methods=["POST", "GET"])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        if book.image:
            try:
                delete_s3_key(book.image)
            except Exception:
                current_app.logger.warning("Could not delete S3 key %s", book.image)
        database.session.delete(book)
        database.session.commit()
        flash("Libro eliminado.", "success")
        return redirect(url_for("books.biblioteca"))

    return render_template("books/delete_book.html", book=book)
