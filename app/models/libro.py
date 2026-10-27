from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .autor import Autor
    from .categoria import Categoria
    from .prestamo import Prestamo

libro_categoria = Table(
    "libro_categoria",
    Base.metadata,
    Column("libro_id", ForeignKey("libros.id", ondelete="CASCADE"), primary_key=True),
    Column("categoria_id", ForeignKey("categorias.id", ondelete="CASCADE"), primary_key=True),
)

LibroCategoria = libro_categoria


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, index=True, nullable=False)
    anio_publicacion: Mapped[int] = mapped_column(nullable=False)
    ejemplares: Mapped[int] = mapped_column(default=1, nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("autores.id"), nullable=False)

    autor: Mapped["Autor"] = relationship(back_populates="libros", lazy="selectin")
    categorias: Mapped[list["Categoria"]] = relationship(
        secondary=libro_categoria,
        back_populates="libros",
        lazy="selectin"
    )
    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="libro", lazy="selectin")

    @property
    def disponibles(self) -> int:
        prestamos_sin_devolver = sum(1 for p in self.prestamos if p.fecha_devolucion is None)
        return max(0, self.ejemplares - prestamos_sin_devolver)
