# api/endpoints.py

from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Dict, Any
from . import crud
from utils.auth import login_user
from utils.logger import log_operation
import secrets

router = APIRouter()
security = HTTPBasic()

# --- Autenticación ---
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica las credenciales del usuario."""
    is_correct_user = login_user(credentials.username, credentials.password)
    if not is_correct_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- Rutas Públicas ---

@router.get("/books", response_model=List[crud.Book])
def list_books():
    """Obtiene una lista de todos los libros."""
    log_operation("GUEST", "LIST_BOOKS")
    return crud.get_all_books()

@router.get("/books/title/{title}", response_model=crud.Book)
def get_book(title: str):
    """Obtiene un libro por su título."""
    book = crud.find_book(title)
    if not book:
        log_operation("GUEST", "GET_BOOK", title, "Failure - Not Found")
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    log_operation("GUEST", "GET_BOOK", title, "Success")
    return book

@router.get("/books/country/{country}")
def get_books_by_country(country: str):
    """Obtiene libros por país."""
    books = crud.find_books_by_country(country)
    log_operation("GUEST", "GET_BY_COUNTRY", f"Country: {country}", f"Found {len(books)} books")
    return {"country": country, "count": len(books), "books": books}

@router.get("/books/suggest/pages/{pages}")
def get_books_by_page_suggestion(pages: int):
    """Sugiere libros por número de páginas."""
    books = crud.suggest_book_by_pages(pages)
    log_operation("GUEST", "SUGGEST_BY_PAGES", f"Pages: {pages}", f"Found {len(books)} suggestions")
    return {"page_target": pages, "count": len(books), "suggestions": books}

# --- Rutas Protegidas ---

@router.post("/books", response_model=crud.Book, status_code=status.HTTP_201_CREATED)
def add_book(book: crud.Book, username: str = Depends(get_current_user)):
    """Añade un nuevo libro (requiere autenticación)."""
    try:
        new_book = crud.add_book(book)
        log_operation(username, "ADD_BOOK", book.title, "Success")
        return new_book
    except ValueError as e:
        log_operation(username, "ADD_BOOK", book.title, f"Failure - {e}")
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/books/{title}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(title: str, username: str = Depends(get_current_user)):
    """Elimina un libro por su título (requiere autenticación)."""
    if not crud.delete_book(title):
        log_operation(username, "DELETE_BOOK", title, "Failure - Not Found")
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    log_operation(username, "DELETE_BOOK", title, "Success")
    return {}

@router.put("/books/{title}", response_model=crud.Book)
def update_book(title: str, new_data: Dict[str, Any] = Body(...), username: str = Depends(get_current_user)):
    """Actualiza un libro (requiere autenticación)."""
    updated_book = crud.update_book(title, new_data)
    if not updated_book:
        log_operation(username, "UPDATE_BOOK", title, "Failure - Not Found")
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    log_operation(username, "UPDATE_BOOK", title, "Success")
    return updated_book