from . import db  
from flask_login import UserMixin
from datetime import datetime

# --- Modelo User  ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime) 
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic') 
    forum_posts = db.relationship('Post', backref='author', lazy='dynamic') 
    def __repr__(self):
        return f'<User {self.name}>'

# --- Modelo Genre ---
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# --- Tabla de Asociación para la relación Many-to-Many entre Book y Genre ---
books_genres = db.Table('books_have_genres',
    db.Column('book_fk', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('genre_fk', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

# --- Modelo Book  ---
class Book(db.Model):

    __tablename__ = 'books' 
    id = db.Column('book_id', db.Integer, primary_key=True) 
    
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    format = db.Column(db.String(50))
    editorial = db.Column(db.String(100))
    synopsis = db.Column(db.Text)
    image = db.Column(db.String(255)) # URL o path a la imagen
    quantity = db.Column(db.Integer, default=0) # Stock

    genres = db.relationship('Genre', 
                             secondary=books_genres, 
                             lazy='subquery',
                             backref=db.backref('books', lazy=True))

    cart_items = db.relationship('CartItem', backref='book', lazy='dynamic')
    
    def __repr__(self):
        return f'<Book {self.title}>'

# --- Modelo CartItem  ---
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)    
    cantidad = db.Column(db.Integer, default=1, nullable=False)

    def __repr__(self):
        return f'<CartItem User:{self.user_id} Book:{self.book_id}>'