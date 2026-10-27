from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import models 
from .core.database import Base, engine
from .core.exceptions import ErrorAplicacion
from .routes import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Biblioteca",
    description="API RESTful para la gestión de biblioteca: autores, categorías, libros, socios y préstamos.",
    version="1.0"
)


@app.exception_handler(ErrorAplicacion)
async def manejar_error_aplicacion(request: Request, exc: ErrorAplicacion):
    return JSONResponse(
        status_code=exc.codigo,
        content={"detail": exc.mensaje}
    )


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)