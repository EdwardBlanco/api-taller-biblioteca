from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Prestamo, Socio
from ..schemas.socios import SocioActualizar, SocioCrear


def listar(db: Session, skip: int = 0, limit: int = 20, activo: bool | None = None):
    query = select(Socio)
    if activo is not None:
        query = query.where(Socio.activo == activo)
    query = query.order_by(Socio.nombre).offset(skip).limit(limit)
    return db.scalars(query).all()


def obtener(db: Session, socio_id: int):
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("El socio no existe")
    return socio


def crear(db: Session, datos: SocioCrear):
    existente = db.scalar(select(Socio).where(Socio.email == datos.email))
    if existente is not None:
        raise Conflicto("Ya existe un socio con ese correo electrónico")

    socio = Socio(
        nombre=datos.nombre,
        email=datos.email,
        telefono=datos.telefono,
        activo=datos.activo,
    )
    db.add(socio)
    db.commit()
    db.refresh(socio)
    return socio


def actualizar(db: Session, socio_id: int, datos: SocioActualizar):
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("El socio no existe")

    datos_dict = datos.model_dump(exclude_unset=True)
    if "email" in datos_dict and datos_dict["email"] is not None:
        existente = db.scalar(
            select(Socio).where(Socio.email == datos_dict["email"], Socio.id != socio_id)
        )
        if existente is not None:
            raise Conflicto("El correo electrónico ya está registrado por otro socio")

    for campo, valor in datos_dict.items():
        if valor is not None:
            setattr(socio, campo, valor)

    db.commit()
    db.refresh(socio)
    return socio


def eliminar(db: Session, socio_id: int):
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("El socio no existe")

    prestamo_activo = db.scalar(
        select(Prestamo.id)
        .where(Prestamo.socio_id == socio_id, Prestamo.fecha_devolucion.is_(None))
        .limit(1)
    )
    if prestamo_activo is not None:
        raise Conflicto("No se puede eliminar el socio porque tiene préstamos sin devolver")

    prestamo_historial = db.scalar(
        select(Prestamo.id).where(Prestamo.socio_id == socio_id).limit(1)
    )
    if prestamo_historial is not None:
        socio.activo = False
        db.commit()
    else:
        db.delete(socio)
        db.commit()


def listar_prestamos_socio(db: Session, socio_id: int, estado: str | None = None):
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("El socio no existe")

    hoy = date.today()
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id)

    if estado == "activo":
        consulta = consulta.where(
            Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite >= hoy
        )
    elif estado == "vencido":
        consulta = consulta.where(
            Prestamo.fecha_devolucion.is_(None), Prestamo.fecha_limite < hoy
        )
    elif estado == "devuelto":
        consulta = consulta.where(Prestamo.fecha_devolucion.is_not(None))

    consulta = consulta.order_by(Prestamo.fecha_prestamo.desc())
    return db.scalars(consulta).all()
