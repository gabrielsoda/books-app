# book_app/utils/checker.py

import os
import json
from datetime import datetime


DATA_DIR = "data"
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

def get_metadata():
    """Lee el archivo de metadatos."""
    if not os.path.exists(METADATA_FILE):
        return {"books_json_downloaded": False, "images_downloaded": False, "last_checked": None}
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

def update_metadata(key, value):
    """Actualiza un valor en el archivo de metadatos."""
    metadata = get_metadata()
    metadata[key] = value
    metadata["last_checked"] = datetime.now().isoformat()
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)

def check_data_exists():
    """
    Verifica si los archivos de datos (JSON y al menos una imagen) existen.
    Retorna un diccionario con el estado.
    """
    metadata = get_metadata()
    books_exist = os.path.exists(BOOKS_FILE)
    images_dir_exists = os.path.exists(IMAGES_DIR) and len(os.listdir(IMAGES_DIR)) > 0

    # Actualiza metadatos si los archivos existen pero no estaban registrados
    if books_exist and not metadata.get("books_json_downloaded"):
        update_metadata("books_json_downloaded", True)
    
    if images_dir_exists and not metadata.get("images_downloaded"):
        update_metadata("images_downloaded", True)

    return {
        "books_json": books_exist,
        "images": images_dir_exists
    }