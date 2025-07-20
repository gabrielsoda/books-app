# book_app/README.md

# Book App - Gestión de Libros en Terminal

Este es un proyecto completo en Python para gestionar una colección de libros a través de una API backend con FastAPI y una interfaz de línea de comandos (CLI) interactiva.

## 📦 Tecnologías

*   **Backend:** FastAPI
*   **Base de datos:** `books.json` (archivo local)
*   **Frontend:** Menú en terminal con `questionary`
*   **Visualización de imágenes:** `term-image`
*   **Otras librerías:** `uvicorn`, `pydantic`, `httpx`, `bcrypt`, `rich`, `requests`

## 🚀 Cómo empezar

### 1. Prerrequisitos

*   Python 3.8 o superior.
*   Una terminal que soporte imágenes (como iTerm2 en macOS o Windows Terminal con WSL).

### 2. Instalación

1.  **Clona o descarga este proyecto.**

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Ejecución

El proyecto consta de dos componentes principales que deben ejecutarse en terminales separadas:

#### A. Iniciar el Backend (API)

En una terminal, ejecuta el servidor de FastAPI:

```bash
uvicorn api.main:app --reload
```

El servidor estará disponible en http://127.0.0.1:8000.
#### B. Iniciar la Interfaz de Usuario (CLI)
En otra terminal, ejecuta el menú interactivo:

