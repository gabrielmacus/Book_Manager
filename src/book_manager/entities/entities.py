from datetime import date


def _validar_texto(valor: str, campo: str) -> str:
    """Valida que el valor sea un texto no vacío y lo devuelve sin espacios."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío.")
    return valor.strip()


def _validar_entero(valor: int, campo: str, minimo: int) -> int:
    """Valida que el valor sea un entero mayor o igual a `minimo`."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ValueError(
            f"{campo} debe ser un entero mayor o igual a {minimo}."
        )
    return valor


def _validar_valor(valor: float, campo: str) -> float:
    """Valida que el valor sea un número mayor a 0."""
    es_numero = isinstance(valor, (int, float)) and not isinstance(valor, bool)
    if not es_numero or valor <= 0:
        raise ValueError(f"{campo} debe ser un número mayor a 0.")
    return float(valor)


class EntidadBase:
    """Entidad identificada por un id entero positivo."""

    def __init__(self, id: int) -> None:
        self.id = id

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        self._id = _validar_entero(valor, "El id", 1)


class Genero(EntidadBase):
    """Categoría literaria a la que pertenece un libro."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre")


class Editorial(EntidadBase):
    """Proveedor o distribuidora que provee los libros a la librería."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre")


class Moneda(EntidadBase):
    """Moneda en la que se puede expresar un precio (ARS, USD, etc.)."""

    def __init__(self, id: int, codigo: str, nombre: str) -> None:
        super().__init__(id)
        self.codigo = codigo
        self.nombre = nombre

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        self._codigo = _validar_texto(valor, "El código").upper()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre")


class TipoCotizacion(EntidadBase):
    """Tipo de cotización del dólar (Oficial, Blue, MEP, etc.)."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre")


class Libro(EntidadBase):
    """Título del catálogo de la librería."""

    def __init__(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
    ) -> None:
        super().__init__(id)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial_id = editorial_id
        self.genero_id = genero_id

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        self._isbn = _validar_texto(valor, "El ISBN")

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = _validar_texto(valor, "El título")

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self._autor = _validar_texto(valor, "El autor")

    @property
    def editorial_id(self) -> int:
        return self._editorial_id

    @editorial_id.setter
    def editorial_id(self, valor: int) -> None:
        self._editorial_id = _validar_entero(valor, "El id de editorial", 1)

    @property
    def genero_id(self) -> int:
        return self._genero_id

    @genero_id.setter
    def genero_id(self, valor: int) -> None:
        self._genero_id = _validar_entero(valor, "El id de género", 1)


class Precio(EntidadBase):
    """Valor monetario de un libro en una moneda determinada."""

    def __init__(
        self, id: int, libro_id: int, moneda_id: int, valor: float
    ) -> None:
        super().__init__(id)
        self.libro_id = libro_id
        self.moneda_id = moneda_id
        self.valor = valor

    @property
    def libro_id(self) -> int:
        return self._libro_id

    @libro_id.setter
    def libro_id(self, valor: int) -> None:
        self._libro_id = _validar_entero(valor, "El id de libro", 1)

    @property
    def moneda_id(self) -> int:
        return self._moneda_id

    @moneda_id.setter
    def moneda_id(self, valor: int) -> None:
        self._moneda_id = _validar_entero(valor, "El id de moneda", 1)

    @property
    def valor(self) -> float:
        return self._valor

    @valor.setter
    def valor(self, valor: float) -> None:
        self._valor = _validar_valor(valor, "El valor")


class Stock:
    """Cantidad disponible de un libro, identificada por el id del libro."""

    def __init__(self, libro_id: int, cantidad: int) -> None:
        self.libro_id = libro_id
        self.cantidad = cantidad

    @property
    def libro_id(self) -> int:
        return self._libro_id

    @libro_id.setter
    def libro_id(self, valor: int) -> None:
        self._libro_id = _validar_entero(valor, "El id de libro", 1)

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        self._cantidad = _validar_entero(valor, "La cantidad", 0)


class CotizacionDolar:
    """Valor del dólar para un tipo de cotización en una fecha determinada."""

    def __init__(self, tipo_id: int, fecha: date, valor: float) -> None:
        self.tipo_id = tipo_id
        self.fecha = fecha
        self.valor = valor

    @property
    def tipo_id(self) -> int:
        return self._tipo_id

    @tipo_id.setter
    def tipo_id(self, valor: int) -> None:
        self._tipo_id = _validar_entero(valor, "El id de tipo", 1)

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser de tipo date.")
        self._fecha = valor

    @property
    def valor(self) -> float:
        return self._valor

    @valor.setter
    def valor(self, valor: float) -> None:
        self._valor = _validar_valor(valor, "El valor")
