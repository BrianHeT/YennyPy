import os
from datetime import datetime
from app import create_app, database
from app.models import Book


app = create_app()

with app.app_context():
    print("Eliminando libros existentes...")
    Book.query.delete()

    print("Sembrando nuevos libros...")
    
    book_data = [
        {
            'title': 'AMANECER EN LA COSECHA (JUEGOS HAMBRE 5)',
            'price': 34999, 
            'release_date': datetime(2025, 3, 1),
            'format': 'Libros',
            'editorial': 'Molino',
            'author_name': 'Suzane Collins',
            'synopsis': '¡Llega la increible quinta entrega de la saga Los Juegos del Hambre! Cuando te roban todo lo que amas, ¿queda algo por lo que luchar? Amanece el día de los Quincuagésimos Juegos del Hambre y el miedo atenaza a los distritos de Panem...',
            'image': 'amanecer_en_la_cosecha.jpg',
            'quantity': 10
        },
        {
            'title': 'ESTE DOLOR NO ES MIO',
            'price': 32900, 
            'release_date': datetime(2018, 2, 1),
            'format': 'Libros',
            'editorial': 'Grupal/gaia',
            'author_name': 'Mark Wolynn',
            'synopsis': 'DEPRESIÓN. ANSIEDAD. DOLORES CRÓNICOS. FOBIAS. PENSAMIENTOS OBSESIVOS. La evidencia científica muestra que los traumas pueden ser heredados. Existen pruebas fiables de que muchos problemas crónicos o de largo plazo pueden no tener su origen en nuestras vivencias inmediatas...',
            'image': 'este_dolor_no_es_mio.jpg',
            'quantity': 5
        },
        {
            'title': 'LA VEGETARIANA',
            'price': 23900, 
            'release_date': datetime(2024, 10, 1),
            'format': 'Libros',
            'editorial': 'Random House',
            'author_name': 'Han Kang',
            'synopsis': 'Hasta ahora, Yeonghye ha sido la esposa diligente y discreta que su marido siempre ha deseado. Todo cambia cuando unas pesadillas brutales y sanguinarias empiezan a despertarla por las noches...',
            'image': 'la_vegetariana.jpg',
            'quantity': 15
        },
        {
            'title': 'EL BUEN MAL',
            'price': 24999,
            'release_date': datetime(2018, 2, 1),
            'format': 'Libros',
            'editorial': 'Random House',
            'author_name': 'Samanta SCHWEBLIN',
            'synopsis': 'Samanta Schweblin, la maestra del cuento contemporáneo latinoamericano, regresa con un libro destinado a convertirse en un clásico global. Magnéticos e irresistibles. En cada uno de los cuentos de «El buen mal», Samanta Schweblin nos abduce a otra dimensión...',
            'image': 'el_buen_mal.jpg',
            'quantity': 8
        },
        {
            'title': 'MI NOMBRE ES EMILIA DEL VALLE',
            'price': 34499, 
            'release_date': datetime(2025, 4, 1),
            'format': 'Libros',
            'editorial': 'Sudamericana',
            'author_name': 'Isabel Allende',
            'synopsis': 'Una inolvidable historia de amor y de guerra protagonizada por una mujer que, enfrentada a los mayores desafíos, sobrevive y se reinventa. San Francisco, 1866: una monja irlandesa, embarazada y abandonada por un aristócrata chileno...',
            'image': 'mi_nombre_es_emilia_del_valle.jpg',
            'quantity': 12
        },
        {
            'title': 'LA CASA NEVILLE 3. YO SOY EL VIENTO',
            'price': 32900, 
            'release_date': datetime(2024, 11, 1),
            'format': 'Libros',
            'editorial': 'Planeta',
            'author_name': 'Florencia Bonelli',
            'synopsis': 'Manon Neville ha caído en la trampa hábilmente urdida por su pérfido cuñado Julian Porter-White. Con su amado Alexander Blackraven a miles de millas de Londres, se enfrenta a un peligro inminente, quizás a la muerte...',
            'image': 'la_casa_neville_3.jpg',
            'quantity': 7
        },
    ]

    # Iterar sobre los datos y crear objetos Book
    for data in book_data:
        book = Book(
            title=data["title"],
            price=data["price"],
            release_date=data["release_date"],
            format=data["format"],
            editorial=data["editorial"],
            author_name=data["author_name"],
            synopsis=data["synopsis"],
            image=data["image"],
            quantity=data["quantity"]
        )
        database.session.add(book)


# 2.1. Usuario Administrador
    admin_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
    admin_user = User(
        name='Admin',
        email='admin@yenny.com',
        password_hash=admin_password,
        is_admin=True # ⬅ Define como administrador
    )
    database.session.add(admin_user)
    database.session.commit()
    print(f"¡Listo! Se han agregado {len(book_data)} libros.")