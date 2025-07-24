# book_app/cli/display.py

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from term_image.image import from_file
from typing import Optional

# Definición de variables globales
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
console = Console()

def display_book(book: dict, with_image: bool = True):
    """Muestra la información de un libro de forma atractiva."""
    if not book:
        console.print("[red]No se encontró información del libro.[/red]")
        return
    
    info_panel = Panel(
        f"[bold]Autor:[/bold] {book.get('author')}\n"
        f"[bold]País:[/bold] {book.get('country')}\n"
        f"[bold]Idioma:[/bold] {book.get('language')}\n"
        f"[bold]Año:[/bold] {book.get('year')}\n"
        f"[bold]Páginas:[/bold] {book.get('pages')}\n"
        f"[bold]Enlace:[/bold] [link={book.get('link')}]{book.get('link')}[/link]",
        title=f"[bold cyan]{book.get('title')}[/bold cyan]",
        border_style="green",
        expand=False
    )
    console.print(info_panel)

    if with_image:
        display_image(book.get('imageLink'))

def display_image(image_link_path: Optional[str]):
    """Muestra la imagen de portada en la terminal."""
    if not image_link_path:
        console.print("[yellow]Este libro no tiene una imagen asociada.[/yellow]")
        return

    image_filename = os.path.basename(image_link_path)
    image_path = os.path.join(IMAGES_DIR, image_filename)

    if not os.path.exists(image_path):
        console.print(f"[yellow]Advertencia: No se encontró el archivo de imagen '{image_filename}' en '{IMAGES_DIR}'.[/yellow]")
        return
    
    try:
        console.print("Cargando imagen de portada...")
        image = from_file(image_path, width=70)
        image.draw()
    except Exception as e:
        console.print("[red]No se pudo mostrar la imagen. Es posible que tu terminal no sea compatible.[/red]")
        console.print(f"[red]Error: {e}[/red]")

def display_book_list(books: list):
    """Muestra una lista de libros en una tabla."""
    if not books:
        console.print("[yellow]No se encontraron libros.[/yellow]")
        return
        
    table = Table(title="Lista de Libros", show_header=True, header_style="bold magenta")
    table.add_column("Título", style="cyan", no_wrap=True)
    table.add_column("Autor", style="green")
    table.add_column("Año", justify="right")
    table.add_column("Páginas", justify="right")

    for book in books:
        table.add_row(book['title'], book['author'], str(book['year']), str(book['pages']))
    
    console.print(table)