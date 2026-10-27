from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]
sessionDep = SessionDep


class Paginacion:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Registros a omitir"),
        limit: int = Query(20, ge=1, le=100, description="Límite de registros por página"),
    ):
        self.skip = skip
        self.limit = limit


PaginacionDep = Annotated[Paginacion, Depends()]