# api/main.py

from fastapi import FastAPI
from . import endpoints

app = FastAPI(
    title="Book App API",
    description="API para gestionar una colección de libros.",
    version="1.0.0"
)

# Incluir las rutas definidas en endpoints.py
app.include_router(endpoints.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Book App. Visita /docs para la documentación."}

# Esto permite ejecutar con `python api/main.py` aunque se recomienda `uvicorn`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)