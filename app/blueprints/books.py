from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required
from app.utils.decorators import admin_required
from app.extensions import database
from app.models import Book, Author, Genre
from app.bookforms import BookForm

bp_books = Blueprint("books", __name__, url_prefix="/books")

# ---- LISTADO PÚBLICO ----
@bp_books.route("/")
def list_books():
    books = Book.query.all()
    return render_template("books/list.html", books=books)

# ---- DETALLE PÚBLICO ----
@bp_books.route("/<int:book_id>")
def details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("books/details.html", book=book)

# ---- CREAR LIBRO (ADMIN) ----
@bp_books.route("/create", methods=["GET", "POST"])
@admin_required
def create_book():
    form = BookForm()

    form.author_id.choices = [(0, "Sin autor")] + [
        (a.id, a.name) for a in Author.query.all()
    ]

    form.genres.choices = [
        (g.id, g.name) for g in Genre.query.all()
    ]

    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            price=form.price.data,
            release_date=form.release_date.data,
            format=form.format.data,
            editorial=form.editorial.data,
            synopsis=form.synopsis.data,
            image=form.image.data,
            quantity=form.quantity.data,
            author_id=form.author_id.data or None,
            author_name=form.author_name.data
        )

        new_book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()

        database.session.add(new_book)
        database.session.commit()

        return redirect(url_for("books.list_books"))

    return render_template("books/create.html", form=form)

# ---- EDITAR LIBRO (ADMIN) ----
@bp_books.route("/<int:book_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)

    form.genres.choices = [(g.id, g.name) for g in Genre.query.all()]
    form.author_id.choices = [(0, "Sin autor")] + [(a.id, a.name) for a in Author.query.all()]

    if form.validate_on_submit():
        form.populate_obj(book)
        book.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        database.session.commit()
        return redirect(url_for("books.details", book_id=book.id))

    return render_template("books/edit.html", form=form, book=book)

# ---- ELIMINAR LIBRO (ADMIN) ----
@bp_books.route("/<int:book_id>/delete", methods=["POST"])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    database.session.delete(book)
    database.session.commit()
    return redirect(url_for("books.list_books"))
