class ErrorAplicacion(Exception):
    codigo: int = 400

    def __init__(self, mensaje: str = "Error en la aplicación"):
        self.mensaje = mensaje
        super().__init__(self.mensaje)


class NoEncontrado(ErrorAplicacion):
    codigo: int = 404

    def __init__(self, mensaje: str = "El recurso no existe"):
        super().__init__(mensaje)


class Conflicto(ErrorAplicacion):
    codigo: int = 409

    def __init__(self, mensaje: str = "Conflicto con el recurso"):
        super().__init__(mensaje)


class ReglaNegocio(ErrorAplicacion):
    codigo: int = 422

    def __init__(self, mensaje: str = "Regla de negocio no cumplida"):
        super().__init__(mensaje)
