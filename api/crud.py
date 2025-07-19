# api/crud.py

import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

DATA_DIR = "data"
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")

# Modelo Pydantic para un libro
class Book(BaseModel):
    author: str
    country: str
    imageLink: str
    language: str
    link: str
    pages: int
    title: str
    year: int

def get_all_books() -> List[Dict[str, Any]]:
    """Lee y devuelve todos los libros del archivo JSON."""
    if not os.path.exists(BOOKS_FILE):
        return []
    with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_all_books(books: List[Dict[str, Any]]):
    """Guarda la lista completa de libros en el archivo JSON."""
    with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4)

def find_book(title: str) -> Optional[Dict[str, Any]]:
    """Encuentra un libro por su título."""
    books = get_all_books()
    for book in books:
        if book['title'].lower() == title.lower():
            return book
    return None

def add_book(book_data: Book) -> Dict[str, Any]:
    """Añade un nuevo libro a la base de datos."""
    books = get_all_books()
    if find_book(book_data.title):
        raise ValueError("El libro con este título ya existe.")
    
    books.append(book_data.model_dump())
    save_all_books(books)
    return book_data.model_dump()

def delete_book(title: str) -> bool:
    """Elimina un libro por su título."""
    books = get_all_books()
    book_to_delete = find_book(title)
    if not book_to_delete:
        return False
        
    books.remove(book_to_delete)
    save_all_books(books)
    return True

def update_book(title: str, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Actualiza los datos de un libro existente."""
    books = get_all_books()
    for i, book in enumerate(books):
        if book['title'].lower() == title.lower():
            # Actualiza solo los campos proporcionados
            updated_book_data = book.copy()
            updated_book_data.update(new_data)
            
            # Valida con Pydantic antes de guardar
            validated_book = Book(**updated_book_data)
            books[i] = validated_book.model_dump()
            save_all_books(books)
            return books[i]
    return None

def find_books_by_country(country: str) -> List[Dict[str, Any]]:
    """Encuentra todos los libros de un país específico."""
    books = get_all_books()
    return [book for book in books if book['country'].lower() == country.lower()]

def suggest_book_by_pages(page_count: int) -> List[Dict[str, Any]]:
    """Sugiere libros con la cantidad de páginas más cercana a la dada."""
    books = get_all_books()
    if not books:
        return []

    # Calcula la diferencia de páginas para cada libro
    for book in books:
        book['page_diff'] = abs(book['pages'] - page_count)

    # Encuentra la diferencia mínima
    min_diff = min(book['page_diff'] for book in books)

    # Filtra los libros que tienen esa diferencia mínima
    closest_books = [book for book in books if book['page_diff'] == min_diff]
    
    # Limpia la clave temporal 'page_diff' antes de devolver
    for book in closest_books:
        del book['page_diff']

    return closest_books