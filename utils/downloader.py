# book_app/utils/downloader.py

import os
import json
import requests
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from concurrent.futures import ThreadPoolExecutor

from .checker import update_metadata
from .logger import log_operation

DATA_DIR = "data"
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
BOOKS_URL = "https://raw.githubusercontent.com/benoitvallon/100-best-books/master/books.json"
IMAGE_URL_PREFIX = "https://raw.githubusercontent.com/benoitvallon/100-best-books/master/static/"

def download_file(url, dest_path, progress, task):
    """Descarga un único archivo con barra de progreso."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        progress.update(task, total=total_size)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                progress.update(task, advance=len(chunk))
        return True
    except requests.RequestException as e:
        print(f"Error descargando {url}: {e}")
        log_operation("SYSTEM", "DOWNLOAD_ERROR", url, str(e))
        return False

def download_books_json():
    """Descarga el archivo books.json."""
    print("Descargando la base de datos de libros (books.json)...")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with Progress(
        TextColumn("[bold cyan]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("books.json", total=None)
        if download_file(BOOKS_URL, BOOKS_FILE, progress, task):
            update_metadata("books_json_downloaded", True)
            log_operation("SYSTEM", "DOWNLOAD_JSON", "books.json", "Success")
            print("✅ 'books.json' descargado con éxito.")
            return True
    print("❌ No se pudo descargar 'books.json'.")
    return False


def download_image(book, progress, task):
    """Descarga la imagen de un libro."""
    image_link_path = book.get('imageLink') # e.g., 'images/things-fall-apart.jpg'
    if not image_link_path:
        return False, "No image link"

    # Extraemos solo el nombre del archivo para evitar duplicar la carpeta 'images'
    image_filename = os.path.basename(image_link_path)
    
    image_url = os.path.join(IMAGE_URL_PREFIX, image_link_path) # La URL de origen sí usa la ruta completa
    dest_path = os.path.join(IMAGES_DIR, image_filename) # La ruta de destino usa solo el nombre del archivo

    if os.path.exists(dest_path):
        progress.update(task, advance=1)
        return True, "Already exists"
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        progress.update(task, advance=1)
        return True, "Downloaded"
    except requests.RequestException:
        progress.update(task, advance=1)
        return False, "Download failed"

def download_all_images():
    """Descarga todas las imágenes de los libros si no existen."""
    if not os.path.exists(BOOKS_FILE):
        print("❌ 'books.json' no encontrado. Descárgalo primero.")
        return False
        
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    with open(BOOKS_FILE, "r", encoding="utf-8") as f:
        books = json.load(f)
    
    print(f"Verificando y descargando {len(books)} imágenes de portadas...")
    with Progress() as progress:
        task = progress.add_task("[green]Descargando imágenes...", total=len(books))
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(lambda book: download_image(book, progress, task), books))

    update_metadata("images_downloaded", True)
    log_operation("SYSTEM", "DOWNLOAD_IMAGES", "All images", "Success")
    print("✅ Proceso de descarga de imágenes finalizado.")
    return True

def check_and_download_data():
    """Función principal que comprueba y descarga todos los datos necesarios."""
    from .checker import check_data_exists # Importación local para evitar ciclo
    
    print("--- Verificación de Datos Iniciales ---")
    status = check_data_exists()
    
    if not status["books_json"]:
        print("⚠️  'books.json' no encontrado.")
        if not download_books_json():
             print("🚨 Error crítico: No se pudo obtener la base de datos. El programa no puede continuar.")
             exit()
    else:
        print("✔️  'books.json' ya existe.")

    if not status["images"]:
        print("⚠️  Imágenes de portadas no encontradas.")
        download_all_images()
    else:
        print("✔️  El directorio de imágenes ya existe.")
    print("--- Verificación Finalizada --- \n")