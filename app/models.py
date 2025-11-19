from . import database 
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# --- Modelo User  ---
class User(UserMixin, database.Model):
    __tablename__ = 'users'

    id = database.Column(database.Integer, primary_key=True) 
    name = database.Column(database.String(100), nullable=False)
    email = database.Column(database.String(120), unique=True, nullable=False)
    password_hash = database.Column(database.String(255), nullable=False)
    is_admin = database.Column(database.Boolean, default=False)
    email_verified_at = database.Column(database.DateTime) 
    cart_items = database.relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    forum_posts = database.relationship('Post', backref='author', lazy='dynamic') 
    
    def __repr__(self):
        return f'<User {self.name}>'
    
class Author(database.Model):
    __tablename__ = 'authors'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False, unique=True)
    bio = database.Column(database.Text)

    books = database.relationship('Book', backref='author', lazy='dynamic')

# --- Modelo Post (Para el foro/comunidad) ---
class Post(database.Model):
    __tablename__ = 'posts'
    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(140), nullable=False)
    body = database.Column(database.Text, nullable=False)
    timestamp = database.Column(database.DateTime, index=True, default=datetime.utcnow)
    
    user_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False) 
    
    def __repr__(self):
        return f'<Post {self.title}>'

# --- Modelo Genre ---
class Genre(database.Model):
    __tablename__ = 'genres'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(50), unique=True, nullable=False)

# --- Tabla de Asociación para la relación Many-to-Many entre Book y Genre ---
books_genres = database.Table('books_have_genres',
    database.Column('book_fk', database.Integer, database.ForeignKey('books.id'), primary_key=True),  
    database.Column('genre_fk', database.Integer, database.ForeignKey('genres.id'), primary_key=True)
)

# --- Modelo Book  ---
class Book(database.Model):
    __tablename__ = 'books' 
    id = database.Column(database.Integer, primary_key=True) 

    title = database.Column(database.String(255), nullable=False)
    price = database.Column(database.Float, nullable=False)
    release_date = database.Column(database.DateTime, default=datetime.utcnow)
    format = database.Column(database.String(50))
    editorial = database.Column(database.String(100))
    synopsis = database.Column(database.Text)
    image = database.Column(database.String(255)) # URL o path a la imagen
    quantity = database.Column(database.Integer, default=0) 
    author_id = database.Column(database.Integer, database.ForeignKey('authors.id'), nullable=True)
    author_name = database.Column(database.String(100), nullable=False)
    
    genres = database.relationship('Genre', 
                             secondary=books_genres, 
                             lazy='subquery',
                             backref=database.backref('books', lazy=True))

    cart_items = database.relationship('CartItem', back_populates='book', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Book {self.title}>'

# --- Modelo CartItem  ---
class CartItem(database.Model):
    __tablename__ = 'cart_items'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=False)
    book_id = database.Column(database.Integer, database.ForeignKey('books.id'), nullable=False)  
    cantidad = database.Column(database.Integer, default=1, nullable=False)
    
    user = database.relationship('User', back_populates='cart_items')
    book = database.relationship('Book', back_populates='cart_items')

    def __repr__(self):
        return f'<CartItem User:{self.user_id} Book:{self.book_id}>'