# book_app/cli/menu.py

import questionary
import httpx
from rich.console import Console
from rich.panel import Panel
import getpass
from typing import Optional
import time 

from utils.downloader import check_and_download_data
from utils.auth import register_user
from cli.display import display_book, display_book_list

# --- Configuración ---
API_BASE_URL = "http://127.0.0.1:8000"
console = Console()
client = httpx.Client(base_url=API_BASE_URL, timeout=10.0)

# --- Estado de Sesión ---
current_user: Optional[str] = None
current_password: Optional[str] = None

# --- Funciones de Interacción con la API ---

def get_auth():
    if current_user and current_password:
        return (current_user, current_password)
    return None

def handle_api_error(response: httpx.Response):
    """Maneja errores de la API de forma centralizada."""
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", "Error desconocido.")
        except Exception:
            detail = response.text
        console.print(f"[bold red]Error {response.status_code}:[/bold red] {detail}")
        return True
    return False

def cli_list_books():
    try:
        response = client.get("/books")
        if not handle_api_error(response):
            display_book_list(response.json())
    except httpx.ConnectError:
        console.print("[bold red]Error de conexión:[/bold red] No se pudo conectar a la API. ¿El servidor `uvicorn` está en ejecución?")

def cli_get_book():
    title = questionary.text("Introduce el título del libro a buscar:").ask()
    if not title: 
        return
    try:
        response = client.get(f"/books/title/{title}")
        if not handle_api_error(response):
            display_book(response.json())
    except httpx.ConnectError:
        console.print("[bold red]Error de conexión con la API.[/bold red]")

def cli_add_book():
    auth = get_auth()
    if not auth:
        console.print("[yellow]Debes iniciar sesión para añadir un libro.[/yellow]")
        return
    book_data = {
        "title": questionary.text("Título:").ask(),
        "author": questionary.text("Autor:").ask(),
        "country": questionary.text("País:").ask(),
        "language": questionary.text("Idioma:").ask(),
        "year": int(questionary.text("Año:", validate=lambda text: text.isdigit()).ask()),
        "pages": int(questionary.text("Páginas:", validate=lambda text: text.isdigit()).ask()),
        "imageLink": questionary.text("Nombre del archivo de imagen (e.g., 'things-fall-apart.jpg'):").ask(),
        "link": questionary.text("Enlace a Wikipedia:").ask(),
    }
    try:
        response = client.post("/books", json=book_data, auth=auth)
        if not handle_api_error(response):
            console.print(f"[green]Libro '{book_data['title']}' añadido con éxito.[/green]")
            display_book(response.json(), with_image=False)
    except httpx.ConnectError:
        console.print("[bold red]Error de conexión con la API.[/bold red]")

def cli_delete_book():
    auth = get_auth()
    if not auth:
        console.print("[yellow]Debes iniciar sesión para eliminar un libro.[/yellow]")
        return
    title = questionary.text("Introduce el título del libro a eliminar:").ask()
    if not title: 
        return
    if questionary.confirm(f"¿Estás seguro de que quieres eliminar '{title}'?").ask():
        try:
            response = client.delete(f"/books/{title}", auth=auth)
            if not handle_api_error(response):
                console.print(f"[green]Libro '{title}' eliminado con éxito.[/green]")
        except httpx.ConnectError:
            console.print("[bold red]Error de conexión con la API.[/bold red]")

def cli_update_book():
    auth = get_auth()
    if not auth:
        console.print("[yellow]Debes iniciar sesión para actualizar un libro.[/yellow]")
        return
    title = questionary.text("Introduce el título del libro a actualizar:").ask()
    if not title: 
        return
    console.print("[cyan]Introduce los nuevos datos (deja en blanco para no cambiar):[/cyan]")
    new_data = {
        "author": questionary.text("Nuevo autor:").ask(),
        "country": questionary.text("Nuevo país:").ask(),
        "pages": questionary.text("Nuevas páginas:", validate=lambda t: t.isdigit() or t=="").ask(),
    }
    update_payload = {k: (int(v) if k=='pages' else v) for k, v in new_data.items() if v}
    if not update_payload:
        console.print("[yellow]No se proporcionaron datos para actualizar.[/yellow]")
        return
    try:
        response = client.put(f"/books/{title}", json=update_payload, auth=auth)
        if not handle_api_error(response):
            console.print(f"[green]Libro '{title}' actualizado con éxito.[/green]")
            display_book(response.json(), with_image=False)
    except httpx.ConnectError:
        console.print("[bold red]Error de conexión con la API.[/bold red]")

def cli_get_by_country():
    country = questionary.text("Introduce el país:").ask()
    if not country: 
        return
    try:
        response = client.get(f"/books/country/{country}")
        if not handle_api_error(response):
            data = response.json()
            console.print(f"Se encontraron [bold cyan]{data['count']}[/bold cyan] libros de [bold green]{data['country']}[/bold green].")
            if data['count'] > 0:
                display_book_list(data['books'])
    except httpx.ConnectError:
        console.print("[bold red]Error de conexión con la API.[/bold red]")

def cli_suggest_by_pages():
    pages_str = questionary.text("Introduce un número de páginas para buscar sugerencias:", validate=lambda t: t.isdigit()).ask()
    if not pages_str: 
        return
    try:
        response = client.get(f"/books/suggest/pages/{int(pages_str)}")
        if not handle_api_error(response):
            data = response.json()
            suggestions = data.get("suggestions", [])
            console.print(f"Sugerencias para ~[bold cyan]{data['page_target']}[/bold cyan] páginas:")
            if not suggestions:
                console.print("[yellow]No se encontraron sugerencias cercanas.[/yellow]")
                return
            if len(suggestions) == 1:
                display_book(suggestions[0])
            else:
                choices = [f"{book['title']} ({book['pages']} páginas)" for book in suggestions]
                chosen_title_str = questionary.select(
                    "Se encontraron varias coincidencias. Elige una:",
                    choices=choices
                ).ask()
                if chosen_title_str:
                    chosen_title = chosen_title_str.split(' (')[0]
                    chosen_book = next((book for book in suggestions if book['title'] == chosen_title), None)
                    if chosen_book:
                        display_book(chosen_book)
    except httpx.ConnectError:
        console.print("[bold red]Error de conexión con la API.[/bold red]")


# --- Menú de Autenticación y Principal ---

def auth_menu():
    global current_user, current_password
    choice = questionary.select(
        "Bienvenido a Book App. Por favor, inicia sesión o regístrate.",
        choices=["Iniciar Sesión", "Registrarse", "Salir"]
    ).ask()

    if choice == "Iniciar Sesión":
        username = questionary.text("Usuario:").ask()
        if not username: 
            return False # Permite salir del prompt
        password = getpass.getpass("Contraseña: ")
        
        from utils.auth import login_user
        if login_user(username, password):
            console.print(f"[green]¡Bienvenido, {username}![/green]")
            current_user = username
            current_password = password
            return True
        else:
            console.print("[red]Usuario o contraseña incorrectos.[/red]")
            return False
            
    elif choice == "Registrarse":
        username = questionary.text("Nuevo usuario:").ask()
        if not username: 
            return auth_menu() # Vuelve al menú si se cancela
        email = questionary.text("Email:").ask()
        password = getpass.getpass("Contraseña: ")
        if register_user(username, email, password):
            console.print("[green]Usuario registrado con éxito. Ahora puedes iniciar sesión.[/green]")
        else:
            console.print("[red]El nombre de usuario ya existe.[/red]")
        return auth_menu()

    else: # Salir
        return False

def main_menu():
    is_authenticated = current_user is not None
    if is_authenticated:
        console.print(f"Menú Principal (Sesión iniciada como: [bold cyan]{current_user}[/bold cyan])")
    else:
        console.print("[yellow]Menú Principal (Invitado)[/yellow]")
    choices = [
        "Listar todos los libros",
        "Buscar un libro por título",
        "Buscar libros por país",
        "Sugerir libro por n° de páginas",
        "--- Acciones de Administrador ---",
        "Añadir un nuevo libro",
        "Actualizar un libro",
        "Eliminar un libro",
        "-------------------------------",
        "Salir"
    ]

    action = questionary.select(
        "Menú Principal",
        choices=choices
    ).ask()

    if action is None or action == "Salir":
        return False # Termina el bucle

    if action == "Listar todos los libros": 
        cli_list_books()
    elif action == "Buscar un libro por título": 
        cli_get_book()
    elif action == "Buscar libros por país": 
        cli_get_by_country()
    elif action == "Sugerir libro por n° de páginas": 
        cli_suggest_by_pages()
    elif action == "Añadir un nuevo libro": 
        cli_add_book()
    elif action == "Actualizar un libro": 
        cli_update_book()
    elif action == "Eliminar un libro": 
        cli_delete_book()

    # Pausa para que el usuario pueda leer la salida, con lógica especial para imágenes.
    
    # Acciones que pueden mostrar una imagen y necesitan una pausa para el renderizado.
    if action in ["Buscar un libro por título", "Sugerir libro por n° de páginas"]:
        try:
            # Esta pausa da tiempo a la terminal para dibujar la imagen.
            time.sleep(0.1)
        except KeyboardInterrupt:
            pass # Si el usuario pulsa Ctrl+C, simplemente continuamos.
        questionary.press_any_key_to_continue().ask()

    # Acciones que muestran tablas largas y también se benefician de una pausa.
    elif action in ["Listar todos los libros", "Buscar libros por país"]:
        questionary.press_any_key_to_continue().ask()
    
    # Las acciones de administrador y otras no necesitan una pausa aquí.
    # --- FIN DE LA CORRECCIÓN FINAL ---

    return True

if __name__ == "__main__":
    console.print(Panel("📚 Book App Manager 📚", style="bold blue", expand=False))
    
    check_and_download_data()

    if auth_menu():
        while main_menu():
            pass
    
    console.print("¡Hasta luego!")