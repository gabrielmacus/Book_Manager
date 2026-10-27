import abc
import csv
import datetime
from datetime import date
from pathlib import Path
from typing import Any, Generic, List, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    PrecioWeb,
    Stock,
    TipoCotizacion,
)
from book_manager.models.models import (
    CotizacionDolarModel,
    EditorialModel,
    GeneroModel,
    LibroModel,
    MonedaModel,
    PrecioModel,
    PrecioWebModel,
    StockModel,
    TipoCotizacionModel,
)

T = TypeVar('T', bound=EntidadBase)
M = TypeVar('M')


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


class _RepositorioDBBase(IRepositorio[T], Generic[T, M]):
    """Base para repositorios de base de datos con clave primaria id."""

    _modelo: type

    def __init__(self, conexion: ConexionDB) -> None:
        """Inicializa el repositorio con la conexión a la base de datos.

        Args:
            conexion (ConexionDB): Conexión a la base de datos.
        """
        self._conexion = conexion

    @abc.abstractmethod
    def _a_entidad(self, modelo: M) -> T:
        """Convierte una instancia de modelo ORM a una entidad de dominio.

        Args:
            modelo (M): Instancia del modelo de SQLAlchemy.

        Returns:
            T: Entidad de dominio correspondiente.
        """
        pass

    @abc.abstractmethod
    def _a_modelo(self, entidad: T) -> M:
        """Convierte una entidad de dominio a un modelo ORM.

        Args:
            entidad (T): Entidad de dominio.

        Returns:
            M: Instancia del modelo de SQLAlchemy correspondiente.
        """
        pass

    @abc.abstractmethod
    def _actualizar_modelo(self, modelo: M, entidad: T) -> None:
        """Actualiza los atributos del modelo existente a partir de la entidad.

        Args:
            modelo (M): Instancia del modelo existente en la sesión.
            entidad (T): Entidad con los nuevos datos.
        """
        pass

    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad en la base de datos.

        Args:
            entidad (T): La entidad a crear.

        Returns:
            T: La entidad creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo ID o hay un
                error de unicidad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                if sesion.get(self._modelo, entidad.id) is not None:
                    raise ValueError(
                        f"Ya existe un registro con el ID {entidad.id}."
                    )
                sesion.add(self._a_modelo(entidad))
            return entidad
        except IntegrityError as e:
            raise ValueError(
                "Error de integridad al crear el registro."
            ) from e

    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad de la base de datos por su ID.

        Args:
            id (int): El ID de la entidad a leer.

        Returns:
            Optional[T]: La entidad si se encuentra, None en caso contrario.
        """
        with self._conexion.transaccion() as sesion:
            modelo = sesion.get(self._modelo, id)
            return self._a_entidad(modelo) if modelo is not None else None

    def leer_todos(self) -> List[T]:
        """Lee todas las entidades de la base de datos ordenadas por ID.

        Returns:
            List[T]: Lista de todas las entidades.
        """
        with self._conexion.transaccion() as sesion:
            modelos = sesion.scalars(
                select(self._modelo).order_by(self._modelo.id)
            ).all()
            return [self._a_entidad(m) for m in modelos]

    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente en la base de datos.

        Args:
            entidad (T): La entidad a actualizar.

        Returns:
            T: La entidad actualizada.

        Raises:
            ValueError: Si no existe el registro o por error de integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                modelo = sesion.get(self._modelo, entidad.id)
                if modelo is None:
                    raise ValueError(
                        f"No existe un registro con el ID {entidad.id}."
                    )
                self._actualizar_modelo(modelo, entidad)
            return entidad
        except IntegrityError as e:
            raise ValueError(
                "Error de integridad al actualizar el registro."
            ) from e

    def eliminar(self, id: int) -> bool:
        """Elimina una entidad de la base de datos por su ID.

        Args:
            id (int): El ID de la entidad a eliminar.

        Returns:
            bool: True si la entidad fue eliminada, False si no se encontró.

        Raises:
            ValueError: Si la entidad tiene registros asociados que impiden
                el borrado.
        """
        try:
            with self._conexion.transaccion() as sesion:
                modelo = sesion.get(self._modelo, id)
                if modelo is None:
                    return False
                sesion.delete(modelo)
            return True
        except IntegrityError as e:
            raise ValueError(
                "No se puede eliminar: tiene registros asociados."
            ) from e


class RepositorioGenero(_RepositorioDBBase[Genero, GeneroModel]):
    """Repositorio de base de datos para Genero."""

    _modelo = GeneroModel

    def _a_entidad(self, modelo: GeneroModel) -> Genero:
        return Genero(modelo.id, modelo.nombre)

    def _a_modelo(self, entidad: Genero) -> GeneroModel:
        return GeneroModel(id=entidad.id, nombre=entidad.nombre)

    def _actualizar_modelo(
        self, modelo: GeneroModel, entidad: Genero
    ) -> None:
        modelo.nombre = entidad.nombre


class RepositorioEditorial(_RepositorioDBBase[Editorial, EditorialModel]):
    """Repositorio de base de datos para Editorial."""

    _modelo = EditorialModel

    def _a_entidad(self, modelo: EditorialModel) -> Editorial:
        return Editorial(modelo.id, modelo.nombre)

    def _a_modelo(self, entidad: Editorial) -> EditorialModel:
        return EditorialModel(id=entidad.id, nombre=entidad.nombre)

    def _actualizar_modelo(
        self, modelo: EditorialModel, entidad: Editorial
    ) -> None:
        modelo.nombre = entidad.nombre


class RepositorioMoneda(_RepositorioDBBase[Moneda, MonedaModel]):
    """Repositorio de base de datos para Moneda."""

    _modelo = MonedaModel

    def _a_entidad(self, modelo: MonedaModel) -> Moneda:
        return Moneda(modelo.id, modelo.codigo, modelo.nombre)

    def _a_modelo(self, entidad: Moneda) -> MonedaModel:
        return MonedaModel(
            id=entidad.id, codigo=entidad.codigo, nombre=entidad.nombre
        )

    def _actualizar_modelo(
        self, modelo: MonedaModel, entidad: Moneda
    ) -> None:
        modelo.codigo = entidad.codigo
        modelo.nombre = entidad.nombre


class RepositorioTipoCotizacion(
    _RepositorioDBBase[TipoCotizacion, TipoCotizacionModel]
):
    """Repositorio de base de datos para TipoCotizacion."""

    _modelo = TipoCotizacionModel

    def _a_entidad(self, modelo: TipoCotizacionModel) -> TipoCotizacion:
        return TipoCotizacion(modelo.id, modelo.nombre)

    def _a_modelo(self, entidad: TipoCotizacion) -> TipoCotizacionModel:
        return TipoCotizacionModel(id=entidad.id, nombre=entidad.nombre)

    def _actualizar_modelo(
        self, modelo: TipoCotizacionModel, entidad: TipoCotizacion
    ) -> None:
        modelo.nombre = entidad.nombre


class RepositorioLibro(_RepositorioDBBase[Libro, LibroModel]):
    """Repositorio de base de datos para Libro."""

    _modelo = LibroModel

    def _a_entidad(self, modelo: LibroModel) -> Libro:
        return Libro(
            modelo.id,
            modelo.isbn,
            modelo.titulo,
            modelo.autor,
            modelo.editorial_id,
            modelo.genero_id,
        )

    def _a_modelo(self, entidad: Libro) -> LibroModel:
        return LibroModel(
            id=entidad.id,
            isbn=entidad.isbn,
            titulo=entidad.titulo,
            autor=entidad.autor,
            editorial_id=entidad.editorial_id,
            genero_id=entidad.genero_id,
        )

    def _actualizar_modelo(
        self, modelo: LibroModel, entidad: Libro
    ) -> None:
        modelo.isbn = entidad.isbn
        modelo.titulo = entidad.titulo
        modelo.autor = entidad.autor
        modelo.editorial_id = entidad.editorial_id
        modelo.genero_id = entidad.genero_id


class RepositorioPrecio(_RepositorioDBBase[Precio, PrecioModel]):
    """Repositorio de base de datos para Precio."""

    _modelo = PrecioModel

    def _a_entidad(self, modelo: PrecioModel) -> Precio:
        return Precio(
            modelo.id,
            modelo.libro_id,
            modelo.moneda_id,
            modelo.valor,
        )

    def _a_modelo(self, entidad: Precio) -> PrecioModel:
        return PrecioModel(
            id=entidad.id,
            libro_id=entidad.libro_id,
            moneda_id=entidad.moneda_id,
            valor=entidad.valor,
        )

    def _actualizar_modelo(
        self, modelo: PrecioModel, entidad: Precio
    ) -> None:
        modelo.libro_id = entidad.libro_id
        modelo.moneda_id = entidad.moneda_id
        modelo.valor = entidad.valor


class RepositorioStock(IRepositorioStock):
    """Repositorio de base de datos para Stock."""

    def __init__(self, conexion: ConexionDB) -> None:
        """Inicializa el repositorio con la conexión a la base de datos.

        Args:
            conexion (ConexionDB): Conexión a la base de datos.
        """
        self._conexion = conexion

    def crear(self, stock: Stock) -> Stock:
        """Crea un nuevo registro de stock.

        Args:
            stock (Stock): El objeto Stock a crear.

        Returns:
            Stock: El objeto Stock creado.

        Raises:
            ValueError: Si ya existe un registro de stock para el libro o
                hay un error de integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                if sesion.get(StockModel, stock.libro_id) is not None:
                    raise ValueError(
                        "Ya existe un registro de stock para el libro "
                        f"{stock.libro_id}."
                    )
                sesion.add(
                    StockModel(
                        libro_id=stock.libro_id, cantidad=stock.cantidad
                    )
                )
            return stock
        except IntegrityError as e:
            raise ValueError("Error de integridad al crear el stock.") from e

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock.

        Returns:
            Optional[Stock]: El objeto Stock si existe, None en caso contrario.
        """
        with self._conexion.transaccion() as sesion:
            modelo = sesion.get(StockModel, libro_id)
            if modelo is None:
                return None
            return Stock(modelo.libro_id, modelo.cantidad)

    def leer_todos(self) -> List[Stock]:
        """Lee todos los registros de stock ordenados por ID de libro.

        Returns:
            List[Stock]: Lista con todos los registros de stock.
        """
        with self._conexion.transaccion() as sesion:
            modelos = sesion.scalars(
                select(StockModel).order_by(StockModel.libro_id)
            ).all()
            return [Stock(m.libro_id, m.cantidad) for m in modelos]

    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un registro de stock existente.

        Args:
            stock (Stock): El objeto Stock con la nueva cantidad.

        Returns:
            Stock: El objeto Stock actualizado.

        Raises:
            ValueError: Si no existe el stock para actualizar o hay un
                error de integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                modelo = sesion.get(StockModel, stock.libro_id)
                if modelo is None:
                    raise ValueError(
                        "No existe un registro de stock para el libro "
                        f"{stock.libro_id}."
                    )
                modelo.cantidad = stock.cantidad
            return stock
        except IntegrityError as e:
            raise ValueError(
                "Error de integridad al actualizar el stock."
            ) from e

    def eliminar(self, libro_id: int) -> bool:
        """Elimina un registro de stock por ID de libro.

        Args:
            libro_id (int): El ID del libro asociado al stock a eliminar.

        Returns:
            bool: True si el stock fue eliminado, False si no se encontró.

        Raises:
            ValueError: Si no se puede eliminar por restricciones de
                integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                modelo = sesion.get(StockModel, libro_id)
                if modelo is None:
                    return False
                sesion.delete(modelo)
            return True
        except IntegrityError as e:
            raise ValueError(
                "No se puede eliminar: tiene registros asociados."
            ) from e


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Repositorio de base de datos para CotizacionDolar."""

    def __init__(self, conexion: ConexionDB) -> None:
        """Inicializa el repositorio con la conexión a la base de datos.

        Args:
            conexion (ConexionDB): Conexión a la base de datos.
        """
        self._conexion = conexion

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una nueva cotización de dólar.

        Args:
            cotizacion (CotizacionDolar): El objeto CotizacionDolar a crear.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar creado.

        Raises:
            ValueError: Si ya existe una cotización para el mismo tipo y
                fecha o hay un error de integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                if (
                    sesion.get(
                        CotizacionDolarModel,
                        (cotizacion.tipo_id, cotizacion.fecha),
                    )
                    is not None
                ):
                    raise ValueError(
                        "Ya existe una cotización para el tipo "
                        f"{cotizacion.tipo_id} "
                        f"en la fecha {cotizacion.fecha}."
                    )
                sesion.add(
                    CotizacionDolarModel(
                        tipo_id=cotizacion.tipo_id,
                        fecha=cotizacion.fecha,
                        valor=cotizacion.valor,
                    )
                )
            return cotizacion
        except IntegrityError as e:
            raise ValueError(
                "Error de integridad al crear la cotización."
            ) from e

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización de dólar por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (date): La fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización si se encuentra, None
                en caso contrario.
        """
        with self._conexion.transaccion() as sesion:
            modelo = sesion.get(CotizacionDolarModel, (tipo_id, fecha))
            if modelo is None:
                return None
            return CotizacionDolar(modelo.tipo_id, modelo.fecha, modelo.valor)

    def leer_historico_por_tipo(
        self, tipo_id: int
    ) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones de un tipo, ordenado por fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Cotizaciones históricas ordenadas por
                fecha.
        """
        with self._conexion.transaccion() as sesion:
            sentencia = (
                select(CotizacionDolarModel)
                .where(CotizacionDolarModel.tipo_id == tipo_id)
                .order_by(CotizacionDolarModel.fecha)
            )
            modelos = sesion.scalars(sentencia).all()
            return [
                CotizacionDolar(m.tipo_id, m.fecha, m.valor) for m in modelos
            ]

    def leer_todos(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones de la base de datos ordenadas por fecha.

        Returns:
            List[CotizacionDolar]: Lista de todas las cotizaciones.
        """
        with self._conexion.transaccion() as sesion:
            sentencia = select(CotizacionDolarModel).order_by(
                CotizacionDolarModel.tipo_id, CotizacionDolarModel.fecha
            )
            modelos = sesion.scalars(sentencia).all()
            return [
                CotizacionDolar(m.tipo_id, m.fecha, m.valor) for m in modelos
            ]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización existente.

        Args:
            cotizacion (CotizacionDolar): La cotización a actualizar.

        Returns:
            CotizacionDolar: El objeto CotizacionDolar actualizado.

        Raises:
            ValueError: Si no existe la cotización para actualizar o hay un
                error de integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                modelo = sesion.get(
                    CotizacionDolarModel,
                    (cotizacion.tipo_id, cotizacion.fecha),
                )
                if modelo is None:
                    raise ValueError(
                        "No existe una cotización para el tipo "
                        f"{cotizacion.tipo_id} "
                        f"en la fecha {cotizacion.fecha}."
                    )
                modelo.valor = cotizacion.valor
            return cotizacion
        except IntegrityError as e:
            raise ValueError(
                "Error de integridad al actualizar la cotización."
            ) from e

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha.

        Args:
            tipo_id (int): El ID del tipo de cotización.
            fecha (date): La fecha de la cotización a eliminar.

        Returns:
            bool: True si la cotización fue eliminada, False si no existía.

        Raises:
            ValueError: Si no se puede eliminar por restricciones de
                integridad.
        """
        try:
            with self._conexion.transaccion() as sesion:
                modelo = sesion.get(CotizacionDolarModel, (tipo_id, fecha))
                if modelo is None:
                    return False
                sesion.delete(modelo)
            return True
        except IntegrityError as e:
            raise ValueError(
                "No se puede eliminar: tiene registros asociados."
            ) from e


class RepositorioPrecioWeb:
    """Repositorio de base de datos para los precios obtenidos de la web."""

    def __init__(self, conexion: ConexionDB) -> None:
        """Inicializa el repositorio con la conexión a la base de datos.

        Args:
            conexion (ConexionDB): Conexión a la base de datos.
        """
        self._conexion = conexion

    def _a_entidad(self, modelo: PrecioWebModel) -> PrecioWeb:
        return PrecioWeb(
            modelo.libro_id,
            modelo.posicion,
            modelo.titulo,
            modelo.url,
            modelo.precio,
            modelo.fecha_extraccion,
            precio_usd=modelo.precio_usd,
            isbn=modelo.isbn,
            imagen_url=modelo.imagen_url,
            formas_pago=modelo.formas_pago,
            descripcion=modelo.descripcion,
            especificaciones=modelo.especificaciones,
            id=modelo.id,
        )

    def crear(self, precio_web: PrecioWeb) -> PrecioWeb:
        """Registra un precio obtenido de la web.

        Args:
            precio_web (PrecioWeb): El precio a registrar.

        Returns:
            PrecioWeb: El precio registrado, con el id asignado por la base.
        """
        with self._conexion.transaccion() as sesion:
            modelo = PrecioWebModel(
                libro_id=precio_web.libro_id,
                posicion=precio_web.posicion,
                titulo=precio_web.titulo,
                url=precio_web.url,
                isbn=precio_web.isbn,
                precio=precio_web.precio,
                precio_usd=precio_web.precio_usd,
                imagen_url=precio_web.imagen_url,
                formas_pago=precio_web.formas_pago,
                descripcion=precio_web.descripcion,
                especificaciones=precio_web.especificaciones,
                fecha_extraccion=precio_web.fecha_extraccion,
            )
            sesion.add(modelo)
            sesion.flush()
            return self._a_entidad(modelo)

    def leer_todos(self) -> List[PrecioWeb]:
        """Lee todos los precios web ordenados por fecha, libro y posición.

        Returns:
            List[PrecioWeb]: Lista con todos los precios web.
        """
        with self._conexion.transaccion() as sesion:
            modelos = sesion.scalars(
                select(PrecioWebModel).order_by(
                    PrecioWebModel.fecha_extraccion,
                    PrecioWebModel.libro_id,
                    PrecioWebModel.posicion,
                )
            ).all()
            return [self._a_entidad(m) for m in modelos]
