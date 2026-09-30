import abc
import csv
import datetime
from pathlib import Path
from typing import Any, Generic, List, Optional, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)

T = TypeVar('T', bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
  """Interfaz para repositorios que manejan entidades con operaciones CRUD básicas."""

  @abc.abstractmethod
  def crear(self, entidad: T) -> T:
    """Crea una nueva entidad en el repositorio.

    Args:
        entidad (T): La entidad a crear.

    Returns:
        T: La entidad creada.

    Raises:
        ValueError: Si ya existe una entidad con el mismo ID.
    """
    pass

  @abc.abstractmethod
  def leer_por_id(self, id: int) -> Optional[T]:
    """Lee una entidad del repositorio por su ID.

    Args:
        id (int): El ID de la entidad a leer.

    Returns:
        Optional[T]: La entidad si se encuentra, None en caso contrario.
    """
    pass

  @abc.abstractmethod
  def leer_todos(self) -> List[T]:
    """Lee todas las entidades del repositorio.

    Returns:
        List[T]: Una lista de todas las entidades.
    """
    pass

  @abc.abstractmethod
  def actualizar(self, entidad: T) -> T:
    """Actualiza una entidad existente en el repositorio.

    Args:
        entidad (T): La entidad a actualizar (debe tener un ID existente).

    Returns:
        T: La entidad actualizada.

    Raises:
        ValueError: Si no se encuentra la entidad para actualizar.
    """
    pass

  @abc.abstractmethod
  def eliminar(self, id: int) -> bool:
    """Elimina una entidad del repositorio por su ID.

    Args:
        id (int): El ID de la entidad a eliminar.

    Returns:
        bool: True si la entidad fue eliminada, False si no se encontró.
    """
    pass


class IRepositorioStock(abc.ABC):
  """Interfaz para repositorios del tipo Stock."""

  @abc.abstractmethod
  def crear(self, stock: Stock) -> Stock:
    """Crea un nuevo registro de stock.

    Args:
        stock (Stock): El objeto Stock a crear.

    Returns:
        Stock: El objeto Stock creado.

    Raises:
        ValueError: Si ya existe un registro de stock para el mismo libro.
    """
    pass

  @abc.abstractmethod
  def leer_por_libro(self, libro_id: int) -> Optional['Stock']:
    """Lee un registro de stock por ID de libro.

    Args:
        libro_id (int): El ID del libro asociado al stock.

    Returns:
        Optional[Stock]: El objeto Stock si se encuentra, None en caso contrario.
    """
    pass

  @abc.abstractmethod
  def actualizar(self, stock: 'Stock') -> 'Stock':
    """Actualiza un registro de stock existente.

    Args:
        stock (Stock): El objeto Stock a actualizar (debe tener un libro_id existente).

    Returns:
        Stock: El objeto Stock actualizado.

    Raises:
        ValueError: Si no se encuentra el stock para actualizar.
    """
    pass

  @abc.abstractmethod
  def eliminar(self, libro_id: int) -> bool:
    """Elimina un registro de stock por ID de libro.

    Args:
        libro_id (int): El ID del libro asociado al stock a eliminar.

    Returns:
        bool: True si el stock fue eliminado, False si no se encontró.
    """
    pass


class IRepositorioCotizacionDolar(abc.ABC):
  """Interfaz para repositorios del tipo RepositorioCotizacionDolar."""

  @abc.abstractmethod
  def crear(self, cotizacion: 'CotizacionDolar') -> 'CotizacionDolar':
    """Crea una nueva cotización de dólar.

    Args:
        cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.

    Returns:
        CotizacionDolar: El objeto CotizacionDolar creado.

    Raises:
        ValueError: Si ya existe una cotización para el mismo tipo y fecha.
    """
    pass

  @abc.abstractmethod
  def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: datetime.date) -> Optional['CotizacionDolar']:
    """Lee una cotización de dólar por tipo y fecha.

    Args:
        tipo_id (int): El ID del tipo de cotización (e.g., 'Oficial', 'Blue').
        fecha (datetime.date): La fecha de la cotización.

    Returns:
        Optional[CotizacionDolar]: La cotización si se encuentra, None en caso contrario.
    """
    pass

  @abc.abstractmethod
  def leer_historico_por_tipo(self, tipo_id: int) -> List['CotizacionDolar']:
    """Lee el histórico de cotizaciones para un tipo específico.

    Args:
        tipo_id (int): El ID del tipo de cotización.

    Returns:
        List[CotizacionDolar]: Una lista de cotizaciones históricas para el tipo dado.
    """
    pass

  @abc.abstractmethod
  def actualizar(self, cotizacion: 'CotizacionDolar') -> 'CotizacionDolar':
    """Actualiza una cotización de dólar existente.

    Args:
        cotizacion (CotizacionDolar): El objeto CotizacionDolar a actualizar.

    Returns:
        CotizacionDolar: El objeto CotizacionDolar actualizado.
    """
    pass

  @abc.abstractmethod
  def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
    """Elimina una cotización de dólar por tipo y fecha.

    Args:
        tipo_id (int): El ID del tipo de cotización.
        fecha (datetime.date): La fecha de la cotización a eliminar.

    Returns:
        bool: True si la cotización fue eliminada, False si no se encontró.
    """
    pass


E = TypeVar("E")


class _RepositorioCsvBase(abc.ABC, Generic[E]):
    """Base que persiste registros en un CSV, identificados por una clave."""

    _CAMPOS: List[str]

    def __init__(self, ruta: Path) -> None:
        self._ruta = ruta

    @abc.abstractmethod
    def _clave(self, registro: E) -> Any:
        """Devuelve la clave que identifica al registro."""

    @abc.abstractmethod
    def _a_fila(self, registro: E) -> dict:
        """Convierte el registro en una fila del CSV."""

    @abc.abstractmethod
    def _desde_fila(self, fila: dict) -> E:
        """Convierte una fila del CSV en un registro."""

    def leer_todos(self) -> List[E]:
        if not self._ruta.exists():
            return []
        with self._ruta.open(newline="", encoding="utf-8") as archivo:
            return [self._desde_fila(fila) for fila in csv.DictReader(archivo)]

    def _guardar(self, registros: List[E]) -> None:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        with self._ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=self._CAMPOS)
            escritor.writeheader()
            escritor.writerows(self._a_fila(r) for r in registros)

    def _leer_por_clave(self, clave: Any) -> Optional[E]:
        return next(
            (r for r in self.leer_todos() if self._clave(r) == clave), None
        )

    def crear(self, registro: E) -> E:
        if self._leer_por_clave(self._clave(registro)) is not None:
            raise ValueError("Ya existe un registro con la misma clave.")
        self._guardar(self.leer_todos() + [registro])
        return registro

    def actualizar(self, registro: E) -> E:
        registros = self.leer_todos()
        for i, existente in enumerate(registros):
            if self._clave(existente) == self._clave(registro):
                registros[i] = registro
                self._guardar(registros)
                return registro
        raise ValueError("No existe un registro con esa clave.")

    def eliminar(self, clave: Any) -> bool:
        registros = self.leer_todos()
        restantes = [r for r in registros if self._clave(r) != clave]
        if len(restantes) == len(registros):
            return False
        self._guardar(restantes)
        return True


class RepositorioCsv(_RepositorioCsvBase[T], IRepositorio[T]):
    """Repositorio CSV para entidades identificadas por id."""

    def _clave(self, registro: T) -> int:
        return registro.id

    def leer_por_id(self, id: int) -> Optional[T]:
        return self._leer_por_clave(id)


class RepositorioGeneroCsv(RepositorioCsv[Genero]):
    _CAMPOS = ["id", "nombre"]

    def _a_fila(self, registro: Genero) -> dict:
        return {"id": registro.id, "nombre": registro.nombre}

    def _desde_fila(self, fila: dict) -> Genero:
        return Genero(int(fila["id"]), fila["nombre"])


class RepositorioEditorialCsv(RepositorioCsv[Editorial]):
    _CAMPOS = ["id", "nombre"]

    def _a_fila(self, registro: Editorial) -> dict:
        return {"id": registro.id, "nombre": registro.nombre}

    def _desde_fila(self, fila: dict) -> Editorial:
        return Editorial(int(fila["id"]), fila["nombre"])


class RepositorioMonedaCsv(RepositorioCsv[Moneda]):
    _CAMPOS = ["id", "codigo", "nombre"]

    def _a_fila(self, registro: Moneda) -> dict:
        return {
            "id": registro.id,
            "codigo": registro.codigo,
            "nombre": registro.nombre,
        }

    def _desde_fila(self, fila: dict) -> Moneda:
        return Moneda(int(fila["id"]), fila["codigo"], fila["nombre"])


class RepositorioTipoCotizacionCsv(RepositorioCsv[TipoCotizacion]):
    _CAMPOS = ["id", "nombre"]

    def _a_fila(self, registro: TipoCotizacion) -> dict:
        return {"id": registro.id, "nombre": registro.nombre}

    def _desde_fila(self, fila: dict) -> TipoCotizacion:
        return TipoCotizacion(int(fila["id"]), fila["nombre"])


class RepositorioLibroCsv(RepositorioCsv[Libro]):
    _CAMPOS = ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"]

    def _a_fila(self, registro: Libro) -> dict:
        return {
            "id": registro.id,
            "isbn": registro.isbn,
            "titulo": registro.titulo,
            "autor": registro.autor,
            "editorial_id": registro.editorial_id,
            "genero_id": registro.genero_id,
        }

    def _desde_fila(self, fila: dict) -> Libro:
        return Libro(
            int(fila["id"]),
            fila["isbn"],
            fila["titulo"],
            fila["autor"],
            int(fila["editorial_id"]),
            int(fila["genero_id"]),
        )


class RepositorioPrecioCsv(RepositorioCsv[Precio]):
    _CAMPOS = ["id", "libro_id", "moneda_id", "valor"]

    def _a_fila(self, registro: Precio) -> dict:
        return {
            "id": registro.id,
            "libro_id": registro.libro_id,
            "moneda_id": registro.moneda_id,
            "valor": registro.valor,
        }

    def _desde_fila(self, fila: dict) -> Precio:
        return Precio(
            int(fila["id"]),
            int(fila["libro_id"]),
            int(fila["moneda_id"]),
            float(fila["valor"]),
        )


class RepositorioStockCsv(_RepositorioCsvBase[Stock], IRepositorioStock):
    """Repositorio CSV de stock, identificado por el id del libro."""

    _CAMPOS = ["libro_id", "cantidad"]

    def _clave(self, registro: Stock) -> int:
        return registro.libro_id

    def _a_fila(self, registro: Stock) -> dict:
        return {"libro_id": registro.libro_id, "cantidad": registro.cantidad}

    def _desde_fila(self, fila: dict) -> Stock:
        return Stock(int(fila["libro_id"]), int(fila["cantidad"]))

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        return self._leer_por_clave(libro_id)


class RepositorioCotizacionDolarCsv(
    _RepositorioCsvBase[CotizacionDolar], IRepositorioCotizacionDolar
):
    """Repositorio CSV de cotizaciones, identificadas por tipo y fecha."""

    _CAMPOS = ["tipo_id", "fecha", "valor"]

    def _clave(self, registro: CotizacionDolar) -> tuple:
        return (registro.tipo_id, registro.fecha)

    def _a_fila(self, registro: CotizacionDolar) -> dict:
        return {
            "tipo_id": registro.tipo_id,
            "fecha": registro.fecha.isoformat(),
            "valor": registro.valor,
        }

    def _desde_fila(self, fila: dict) -> CotizacionDolar:
        return CotizacionDolar(
            int(fila["tipo_id"]),
            datetime.date.fromisoformat(fila["fecha"]),
            float(fila["valor"]),
        )

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        return self._leer_por_clave((tipo_id, fecha))

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        historico = [c for c in self.leer_todos() if c.tipo_id == tipo_id]
        return sorted(historico, key=lambda c: c.fecha)

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        return super().eliminar((tipo_id, fecha))
