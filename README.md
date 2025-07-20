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

El servidor estará disponible en `http://127.0.0.1:8000`.

#### B. Iniciar la Interfaz de Usuario (CLI)

En otra terminal, ejecuta el menú interactivo:

```bash
python -m cli.menu
```

Al iniciar por primera vez, el programa descargará automáticamente la base de datos de libros y las imágenes de las portadas.

Sigue las instrucciones en pantalla para registrarte, iniciar sesión y explorar las funcionalidades.

## ✅ Funcionalidades

*   **CRUD completo de libros:** Añadir, ver, actualizar y eliminar libros.
*   **Autenticación de usuarios:** Sistema de registro e inicio de sesión seguro con contraseñas hasheadas.
*   **Consulta avanzada:** Busca libros por país o recibe sugerencias por número de páginas.
*   **Visualización de portadas:** Muestra las portadas de los libros directamente en la terminal.
*   **Logging:** Todas las operaciones importantes se registran en `logs/app.log`.
*   **Descarga automática de datos:** Los datos iniciales se obtienen de forma automática si no existen localmente.