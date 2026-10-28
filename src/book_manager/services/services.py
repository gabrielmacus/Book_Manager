import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
import functools
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional
import unicodedata

from dotenv import load_dotenv
from pandas import DataFrame
import requests

from book_manager.entities.entities import (
    Auditoria,
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    PrecioWeb,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    IRepositorio,
    IRepositorioCotizacionDolar,
    IRepositorioStock,
    RepositorioAuditoria,
    RepositorioPrecioWeb,
)

REPORTES_DIR = Path(__file__).resolve().parent.parent / "reportes"
SCRAPER_DIR = Path(__file__).resolve().parent.parent / "scraper"
# Argentina no usa horario de verano: siempre es UTC-3.
HORA_ARGENTINA = timezone(timedelta(hours=-3))


def ahora_utc() -> datetime:
    """Retorna la fecha y hora actual en UTC, como se guarda en la base."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def a_hora_local(fecha: datetime) -> datetime:
    """Convierte una fecha guardada en UTC a la hora de Argentina."""
    return (
        fecha.replace(tzinfo=timezone.utc)
        .astimezone(HORA_ARGENTINA)
        .replace(tzinfo=None, microsecond=0)
    )


def _normalizar_titulo(texto: str) -> str:
    """Normaliza un título para comparar palabras sin acentos ni signos."""
    texto_ascii = (
        unicodedata.normalize("NFKD", texto)
        .encode("ascii", "ignore")
        .decode()
    )
    return " ".join(
        "".join(
            caracter if caracter.isalnum() else " "
            for caracter in texto_ascii.upper()
        ).split()
    )


@dataclass
class ComparacionPrecio:
    """Diferencia entre el precio interno y el precio obtenido de la web."""

    libro_id: int
    libro: str
    isbn: str
    precio_interno: float
    precio_web: float
    diferencia: float
    diferencia_porcentual: float
    url: str
    fecha_extraccion: datetime


_servicio_auditoria: Optional["ServicioAuditoria"] = None


def configurar_auditoria(
    servicio: Optional["ServicioAuditoria"],
) -> None:
    """Configura el ServicioAuditoria que usa el decorador @auditar."""
    global _servicio_auditoria
    _servicio_auditoria = servicio


def auditar(
    accion: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorador con parámetro que registra en la auditoría cada operación.

    Args:
        accion (str): Nombre de la acción a registrar en la auditoría.

    Returns:
        Callable: El decorador que envuelve el método auditado.
    """

    def decorador(funcion: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(funcion)
        def envoltura(*args: Any, **kwargs: Any) -> Any:
            args_sin_self = args[1:] if len(args) > 0 else ()
            argumentos = f"args={args_sin_self} kwargs={kwargs}"
            try:
                resultado = funcion(*args, **kwargs)
                if _servicio_auditoria is not None:
                    detalles = f"OK | {argumentos}"
                    if len(detalles) > 500:
                        detalles = detalles[:500]
                    _servicio_auditoria.registrar(accion, detalles)
                return resultado
            except Exception as e:
                if _servicio_auditoria is not None:
                    detalles = f"ERROR: {e} | {argumentos}"
                    if len(detalles) > 500:
                        detalles = detalles[:500]
                    _servicio_auditoria.registrar(accion, detalles)
                raise

        return envoltura

    return decorador


class ServicioAuditoria:
    """Lógica de negocio para la auditoría de operaciones."""

    def __init__(self, repositorio: RepositorioAuditoria) -> None:
        """Inicializa el servicio con el repositorio de auditoría.

        Args:
            repositorio (RepositorioAuditoria): Repositorio de auditoría.
        """
        self._repo = repositorio

    def registrar(self, accion: str, detalles: str = "") -> Auditoria:
        """Crea un registro de auditoría con la fecha actual y lo guarda.

        Args:
            accion (str): Acción realizada.
            detalles (str): Detalles de la operación.

        Returns:
            Auditoria: La auditoría creada.
        """
        auditoria = Auditoria(accion, ahora_utc(), detalles)
        return self._repo.crear(auditoria)

    def obtener_historial(self, limite: int = 50) -> List[Auditoria]:
        """Obtiene las últimas auditorías registradas hasta el límite indicado.

        Args:
            limite (int): Límite de registros a devolver.

        Returns:
            List[Auditoria]: Historial de auditorías, de la más reciente a
                la más vieja.

        Raises:
            ValueError: Si el límite es menor a 1.
        """
        if limite < 1:
            raise ValueError("El límite debe ser mayor o igual a 1.")
        return self._repo.leer_todos()[:limite]


class ServicioPrecioWeb:
    """Compara precios del catálogo con los resultados de Cúspide."""

    # Sin ISBN coincidente, solo se acepta un título casi idéntico.
    SIMILITUD_MINIMA = 0.9

    def __init__(
        self,
        repositorio: RepositorioPrecioWeb,
        repo_libro: IRepositorio[Libro],
        repo_precio: IRepositorio[Precio],
        repo_moneda: IRepositorio[Moneda],
        repo_cotizacion: IRepositorioCotizacionDolar,
        repo_tipo: IRepositorio[TipoCotizacion],
    ) -> None:
        """Inicializa el servicio con los repositorios que necesita."""
        self._repo = repositorio
        self._repo_libro = repo_libro
        self._repo_precio = repo_precio
        self._repo_moneda = repo_moneda
        self._repo_cotizacion = repo_cotizacion
        self._repo_tipo = repo_tipo

    def ejecutar_scraper(self) -> None:
        """Ejecuta el spider en un proceso separado.

        Raises:
            RuntimeError: Si Scrapy finaliza con un error.
        """
        entorno = os.environ.copy()
        entorno["PYTHONPATH"] = str(SCRAPER_DIR.parent.parent)
        resultado = subprocess.run(
            [sys.executable, "-m", "scrapy", "crawl", "cuspide"],
            cwd=SCRAPER_DIR,
            env=entorno,
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            ultimas_lineas = "\n".join(resultado.stderr.splitlines()[-10:])
            raise RuntimeError(
                "Falló la ejecución del scraper:\n" + ultimas_lineas
            )

    def _dolar_oficial(self) -> Optional[float]:
        """Obtiene la cotización más reciente del dólar oficial."""
        tipo = next(
            (
                tipo
                for tipo in self._repo_tipo.leer_todos()
                if tipo.nombre.lower() == "oficial"
            ),
            None,
        )
        if tipo is None:
            return None
        historico = self._repo_cotizacion.leer_historico_por_tipo(tipo.id)
        return historico[-1].valor if historico else None

    def _precio_en_pesos(
        self, valores: Dict[str, float], dolar: Optional[float]
    ) -> Optional[float]:
        """Convierte los precios de una moneda a pesos cuando es posible."""
        if "ARS" in valores:
            return valores["ARS"]
        if "USD" in valores and dolar is not None:
            return round(valores["USD"] * dolar, 2)
        return None

    def _elegir_resultado(
        self, libro: Libro, candidatos: List[PrecioWeb]
    ) -> Optional[PrecioWeb]:
        """Elige por ISBN o por similitud de título el resultado web."""
        coincidencia_isbn = next(
            (
                candidato
                for candidato in candidatos
                if candidato.isbn == libro.isbn
            ),
            None,
        )
        if coincidencia_isbn is not None:
            return coincidencia_isbn
        if not candidatos:
            return None

        titulo = _normalizar_titulo(libro.titulo)
        puntuados = [
            (
                SequenceMatcher(
                    None, titulo, _normalizar_titulo(candidato.titulo)
                ).ratio(),
                candidato,
            )
            for candidato in candidatos
        ]
        similitud, mejor = max(
            puntuados, key=lambda par: (par[0], -par[1].posicion)
        )
        return mejor if similitud >= self.SIMILITUD_MINIMA else None

    def comparar_ultima_extraccion(self) -> List[ComparacionPrecio]:
        """Compara los precios internos con la última extracción web.

        Returns:
            List[ComparacionPrecio]: Comparaciones válidas en pesos.
        """
        precios_web = self._repo.leer_ultima_extraccion()
        if not precios_web:
            return []

        candidatos_por_libro: Dict[int, List[PrecioWeb]] = {}
        for precio_web in precios_web:
            candidatos_por_libro.setdefault(
                precio_web.libro_id, []
            ).append(precio_web)

        codigos_moneda = {
            moneda.id: moneda.codigo
            for moneda in self._repo_moneda.leer_todos()
        }
        valores_por_libro: Dict[int, Dict[str, float]] = {}
        for precio in self._repo_precio.leer_todos():
            codigo = codigos_moneda.get(precio.moneda_id)
            if codigo is not None:
                valores_por_libro.setdefault(precio.libro_id, {})[
                    codigo
                ] = precio.valor

        dolar = self._dolar_oficial()
        comparaciones = []
        for libro in self._repo_libro.leer_todos():
            candidato = self._elegir_resultado(
                libro, candidatos_por_libro.get(libro.id, [])
            )
            precio_interno = self._precio_en_pesos(
                valores_por_libro.get(libro.id, {}), dolar
            )
            if candidato is None or precio_interno is None:
                continue

            diferencia = candidato.precio - precio_interno
            comparaciones.append(
                ComparacionPrecio(
                    libro_id=libro.id,
                    libro=libro.titulo,
                    isbn=libro.isbn,
                    precio_interno=precio_interno,
                    precio_web=candidato.precio,
                    diferencia=round(diferencia, 2),
                    diferencia_porcentual=round(
                        diferencia / precio_interno * 100, 2
                    ),
                    url=candidato.url,
                    fecha_extraccion=candidato.fecha_extraccion,
                )
            )
        return comparaciones

    def generar_alertas(self, umbral_porcentual: float) -> Path:
        """Genera un CSV con las diferencias que superan el umbral.

        Args:
            umbral_porcentual (float): Diferencia porcentual mínima.

        Returns:
            Path: Ruta del archivo CSV generado.
        """
        alertas = [
            comparacion
            for comparacion in self.comparar_ultima_extraccion()
            if abs(comparacion.diferencia_porcentual) > umbral_porcentual
        ]
        REPORTES_DIR.mkdir(parents=True, exist_ok=True)
        ruta = REPORTES_DIR / (
            f"alertas_{datetime.now(HORA_ARGENTINA):%Y%m%d_%H%M%S}.csv"
        )
        encabezados = [
            "libro",
            "isbn",
            "precio_interno",
            "precio_web",
            "diferencia",
            "diferencia_porcentual",
            "url",
            "fecha_extraccion",
        ]
        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=encabezados)
            escritor.writeheader()
            for alerta in alertas:
                escritor.writerow(
                    {
                        "libro": alerta.libro,
                        "isbn": alerta.isbn,
                        "precio_interno": alerta.precio_interno,
                        "precio_web": alerta.precio_web,
                        "diferencia": alerta.diferencia,
                        "diferencia_porcentual": (
                            alerta.diferencia_porcentual
                        ),
                        "url": alerta.url,
                        "fecha_extraccion": a_hora_local(
                            alerta.fecha_extraccion
                        ),
                    }
                )
        return ruta

    @auditar("Ejecutar scraping")
    def ejecutar_scraping(self, umbral_porcentual: float) -> Path:
        """Ejecuta el scraper y genera el CSV de alertas.

        Args:
            umbral_porcentual (float): Diferencia porcentual mínima.

        Returns:
            Path: Ruta del archivo CSV generado.

        Raises:
            ValueError: Si el umbral es negativo o el catálogo está vacío.
            RuntimeError: Si el scraper falla o no obtiene resultados.
        """
        if umbral_porcentual < 0:
            raise ValueError(
                "La diferencia debe ser mayor o igual a 0."
            )
        if not self._repo_libro.leer_todos():
            raise ValueError(
                "No hay libros en el catálogo: cargue los datos antes."
            )
        inicio = ahora_utc()
        self.ejecutar_scraper()
        extraccion = self._repo.leer_ultima_extraccion()
        if not extraccion or extraccion[0].fecha_extraccion < inicio:
            raise RuntimeError(
                "El scraping no obtuvo resultados de Cúspide. "
                "Verifique la conexión e intente nuevamente."
            )
        return self.generar_alertas(umbral_porcentual)

    @auditar("Generar reporte Excel")
    def generar_reporte_excel(self) -> Path:
        """Genera un archivo Excel con la comparación de precios más reciente.

        Returns:
            Path: Ruta del archivo Excel generado.

        Raises:
            ValueError: Si no hay datos de scraping para comparar.
        """
        comparaciones = self.comparar_ultima_extraccion()
        if not comparaciones:
            raise ValueError(
                "No hay datos de scraping para comparar. "
                "Ejecute primero el scraping."
            )

        datos = {
            "Libro": [c.libro for c in comparaciones],
            "Precio interno": [c.precio_interno for c in comparaciones],
            "Precio web": [c.precio_web for c in comparaciones],
            "Diferencia": [c.diferencia for c in comparaciones],
            "Fecha de extracción": [
                a_hora_local(c.fecha_extraccion) for c in comparaciones
            ],
        }
        df = DataFrame(datos)
        REPORTES_DIR.mkdir(parents=True, exist_ok=True)
        ruta = REPORTES_DIR / (
            f"reporte_{datetime.now(HORA_ARGENTINA):%Y%m%d_%H%M%S}.xlsx"
        )
        df.to_excel(ruta, index=False, sheet_name="Comparación")
        return ruta


class ServicioGenero:
    """Lógica de negocio para la entidad Genero."""

    def __init__(
        self,
        repositorio: IRepositorio[Genero],
        repo_libro: IRepositorio[Libro],
    ) -> None:
        self._repo = repositorio
        self._repo_libro = repo_libro

    def siguiente_id(self) -> int:
        """Retorna el próximo id disponible (el mayor existente más 1)."""
        return max((g.id for g in self._repo.leer_todos()), default=0) + 1

    @auditar("Crear género")
    def crear(self, id: int, nombre: str) -> Genero:
        """Crea un nuevo género validando que el nombre no esté duplicado.

        Args:
            id (int): Identificador único del género.
            nombre (str): Nombre del género.

        Returns:
            Genero: El género creado.

        Raises:
            ValueError: Si ya existe un género con el mismo nombre.
        """
        genero = Genero(id, nombre)
        if any(
            g.nombre.lower() == genero.nombre.lower()
            for g in self._repo.leer_todos()
        ):
            raise ValueError(
                f"Ya existe un género con el nombre "
                f"'{genero.nombre}'."
            )
        return self._repo.crear(genero)

    def obtener_todos(self) -> List[Genero]:
        """Retorna todos los géneros registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Genero]:
        """Retorna un género por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    @auditar("Actualizar género")
    def actualizar(self, id: int, nombre: str) -> Genero:
        """Actualiza el nombre de un género existente.

        Args:
            id (int): Identificador del género a modificar.
            nombre (str): Nuevo nombre del género.

        Returns:
            Genero: El género actualizado.

        Raises:
            ValueError: Si no existe el género, o si el nuevo nombre ya está
                        en uso.
        """
        genero = self._repo.leer_por_id(id)
        if genero is None:
            raise ValueError(f"No existe un género con id {id}.")
        genero.nombre = nombre
        duplicado = any(
            g.nombre.lower() == genero.nombre.lower() and g.id != id
            for g in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe un género con el nombre "
                f"'{genero.nombre}'."
            )
        return self._repo.actualizar(genero)

    @auditar("Eliminar género")
    def eliminar(self, id: int) -> bool:
        """Elimina un género por su id.

        Args:
            id (int): Identificador del género a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.

        Raises:
            ValueError: Si hay libros asociados al género.
        """
        libros = self._repo_libro.leer_todos()
        if any(libro.genero_id == id for libro in libros):
            raise ValueError(
                "No se puede eliminar: tiene libros asociados."
            )
        return self._repo.eliminar(id)


class ServicioEditorial:
    """Lógica de negocio para la entidad Editorial."""

    def __init__(
        self,
        repositorio: IRepositorio[Editorial],
        repo_libro: IRepositorio[Libro],
    ) -> None:
        self._repo = repositorio
        self._repo_libro = repo_libro

    def siguiente_id(self) -> int:
        """Retorna el próximo id disponible (el mayor existente más 1)."""
        return max((e.id for e in self._repo.leer_todos()), default=0) + 1

    @auditar("Crear editorial")
    def crear(self, id: int, nombre: str) -> Editorial:
        """Crea una nueva editorial validando que el nombre no esté duplicado.

        Args:
            id (int): Identificador único de la editorial.
            nombre (str): Nombre de la editorial.

        Returns:
            Editorial: La editorial creada.

        Raises:
            ValueError: Si ya existe una editorial con el mismo nombre.
        """
        editorial = Editorial(id, nombre)
        if any(
            e.nombre.lower() == editorial.nombre.lower()
            for e in self._repo.leer_todos()
        ):
            raise ValueError(
                f"Ya existe una editorial con el nombre "
                f"'{editorial.nombre}'."
            )
        return self._repo.crear(editorial)

    def obtener_todos(self) -> List[Editorial]:
        """Retorna todas las editoriales registradas."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Editorial]:
        """Retorna una editorial por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    @auditar("Actualizar editorial")
    def actualizar(self, id: int, nombre: str) -> Editorial:
        """Actualiza el nombre de una editorial existente.

        Args:
            id (int): Identificador de la editorial a modificar.
            nombre (str): Nuevo nombre de la editorial.

        Returns:
            Editorial: La editorial actualizada.

        Raises:
            ValueError: Si no existe la editorial, o si el nuevo nombre ya
                        está en uso.
        """
        editorial = self._repo.leer_por_id(id)
        if editorial is None:
            raise ValueError(f"No existe una editorial con id {id}.")
        editorial.nombre = nombre
        duplicado = any(
            e.nombre.lower() == editorial.nombre.lower() and e.id != id
            for e in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe una editorial con el nombre "
                f"'{editorial.nombre}'."
            )
        return self._repo.actualizar(editorial)

    @auditar("Eliminar editorial")
    def eliminar(self, id: int) -> bool:
        """Elimina una editorial por su id.

        Args:
            id (int): Identificador de la editorial a eliminar.

        Returns:
            bool: True si fue eliminada, False si no existía.

        Raises:
            ValueError: Si hay libros asociados a la editorial.
        """
        libros = self._repo_libro.leer_todos()
        if any(libro.editorial_id == id for libro in libros):
            raise ValueError(
                "No se puede eliminar: tiene libros asociados."
            )
        return self._repo.eliminar(id)


class ServicioMoneda:
    """Lógica de negocio para la entidad Moneda."""

    def __init__(
        self,
        repositorio: IRepositorio[Moneda],
        repo_precio: IRepositorio[Precio],
    ) -> None:
        self._repo = repositorio
        self._repo_precio = repo_precio

    def siguiente_id(self) -> int:
        """Retorna el próximo id disponible (el mayor existente más 1)."""
        return max((m.id for m in self._repo.leer_todos()), default=0) + 1

    @auditar("Crear moneda")
    def crear(self, id: int, codigo: str, nombre: str) -> Moneda:
        """Crea una nueva moneda validando que el código no esté duplicado.

        Args:
            id (int): Identificador único de la moneda.
            codigo (str): Código ISO de la moneda (ej: 'ARS', 'USD').
            nombre (str): Nombre descriptivo de la moneda.

        Returns:
            Moneda: La moneda creada.

        Raises:
            ValueError: Si ya existe una moneda con el mismo código.
        """
        moneda = Moneda(id, codigo, nombre)
        if any(m.codigo == moneda.codigo for m in self._repo.leer_todos()):
            raise ValueError(
                f"Ya existe una moneda con el código '{moneda.codigo}'."
            )
        return self._repo.crear(moneda)

    def obtener_todos(self) -> List[Moneda]:
        """Retorna todas las monedas registradas."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Moneda]:
        """Retorna una moneda por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    @auditar("Actualizar moneda")
    def actualizar(self, id: int, codigo: str, nombre: str) -> Moneda:
        """Actualiza los datos de una moneda existente.

        Args:
            id (int): Identificador de la moneda a modificar.
            codigo (str): Nuevo código de la moneda.
            nombre (str): Nuevo nombre de la moneda.

        Returns:
            Moneda: La moneda actualizada.

        Raises:
            ValueError: Si no existe la moneda, o si el código ya está en uso.
        """
        moneda = self._repo.leer_por_id(id)
        if moneda is None:
            raise ValueError(f"No existe una moneda con id {id}.")
        moneda.codigo = codigo
        moneda.nombre = nombre
        duplicado = any(
            m.codigo == moneda.codigo and m.id != id
            for m in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe una moneda con el código '{moneda.codigo}'."
            )
        return self._repo.actualizar(moneda)

    @auditar("Eliminar moneda")
    def eliminar(self, id: int) -> bool:
        """Elimina una moneda por su id.

        Args:
            id (int): Identificador de la moneda a eliminar.

        Returns:
            bool: True si fue eliminada, False si no existía.

        Raises:
            ValueError: Si hay precios asociados a la moneda.
        """
        precios = self._repo_precio.leer_todos()
        if any(precio.moneda_id == id for precio in precios):
            raise ValueError(
                "No se puede eliminar: tiene precios asociados."
            )
        return self._repo.eliminar(id)


class ServicioTipoCotizacion:
    """Lógica de negocio para la entidad TipoCotizacion."""

    def __init__(
        self,
        repositorio: IRepositorio[TipoCotizacion],
        repo_cotizacion: IRepositorioCotizacionDolar,
    ) -> None:
        self._repo = repositorio
        self._repo_cotizacion = repo_cotizacion

    def siguiente_id(self) -> int:
        """Retorna el próximo id disponible (el mayor existente más 1)."""
        return max((t.id for t in self._repo.leer_todos()), default=0) + 1

    @auditar("Crear tipo de cotización")
    def crear(self, id: int, nombre: str) -> TipoCotizacion:
        """Crea un tipo de cotización validando que el nombre sea único.

        Args:
            id (int): Identificador único del tipo de cotización.
            nombre (str): Nombre del tipo (ej: 'Oficial', 'Blue', 'MEP').

        Returns:
            TipoCotizacion: El tipo de cotización creado.

        Raises:
            ValueError: Si ya existe un tipo de cotización con el mismo nombre.
        """
        tipo = TipoCotizacion(id, nombre)
        if any(
            t.nombre.lower() == tipo.nombre.lower()
            for t in self._repo.leer_todos()
        ):
            raise ValueError(
                f"Ya existe un tipo de cotización con el nombre "
                f"'{tipo.nombre}'."
            )
        return self._repo.crear(tipo)

    def obtener_todos(self) -> List[TipoCotizacion]:
        """Retorna todos los tipos de cotización registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[TipoCotizacion]:
        """Retorna un tipo de cotización por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    @auditar("Actualizar tipo de cotización")
    def actualizar(self, id: int, nombre: str) -> TipoCotizacion:
        """Actualiza el nombre de un tipo de cotización existente.

        Args:
            id (int): Identificador del tipo a modificar.
            nombre (str): Nuevo nombre del tipo de cotización.

        Returns:
            TipoCotizacion: El tipo de cotización actualizado.

        Raises:
            ValueError: Si no existe el tipo, o si el nombre ya está en uso.
        """
        tipo = self._repo.leer_por_id(id)
        if tipo is None:
            raise ValueError(f"No existe un tipo de cotización con id {id}.")
        tipo.nombre = nombre
        duplicado = any(
            t.nombre.lower() == tipo.nombre.lower() and t.id != id
            for t in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe un tipo de cotización con el nombre "
                f"'{tipo.nombre}'."
            )
        return self._repo.actualizar(tipo)

    @auditar("Eliminar tipo de cotización")
    def eliminar(self, id: int) -> bool:
        """Elimina un tipo de cotización por su id.

        Args:
            id (int): Identificador del tipo de cotización a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.

        Raises:
            ValueError: Si hay cotizaciones asociadas al tipo.
        """
        if self._repo_cotizacion.leer_historico_por_tipo(id):
            raise ValueError(
                "No se puede eliminar: tiene cotizaciones asociadas."
            )
        return self._repo.eliminar(id)


class ServicioLibro:
    """Lógica de negocio para la entidad Libro."""

    def __init__(
        self,
        repositorio: IRepositorio[Libro],
        repo_editorial: IRepositorio[Editorial],
        repo_genero: IRepositorio[Genero],
        repo_precio: IRepositorio[Precio],
        repo_stock: IRepositorioStock,
        repo_precio_web: RepositorioPrecioWeb,
    ) -> None:
        self._repo = repositorio
        self._repo_editorial = repo_editorial
        self._repo_genero = repo_genero
        self._repo_precio = repo_precio
        self._repo_stock = repo_stock
        self._repo_precio_web = repo_precio_web

    def siguiente_id(self) -> int:
        """Retorna el próximo id disponible (el mayor existente más 1)."""
        return max((lib.id for lib in self._repo.leer_todos()), default=0) + 1

    @auditar("Crear libro")
    def crear(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
    ) -> Libro:
        """Crea un nuevo libro con validaciones de integridad referencial.

        Args:
            id (int): Identificador único del libro.
            isbn (str): Código ISBN del libro.
            titulo (str): Título del libro.
            autor (str): Autor del libro.
            editorial_id (int): ID de la editorial asociada.
            genero_id (int): ID del género asociado.

        Returns:
            Libro: El libro creado.

        Raises:
            ValueError: Si el ISBN ya existe, o la editorial/género no existen.
        """
        libro = Libro(id, isbn, titulo, autor, editorial_id, genero_id)
        if any(otro.isbn == libro.isbn for otro in self._repo.leer_todos()):
            raise ValueError(f"Ya existe un libro con el ISBN '{libro.isbn}'.")
        if self._repo_editorial.leer_por_id(editorial_id) is None:
            raise ValueError(f"No existe una editorial con id {editorial_id}.")
        if self._repo_genero.leer_por_id(genero_id) is None:
            raise ValueError(f"No existe un género con id {genero_id}.")
        return self._repo.crear(libro)

    def obtener_todos(self) -> List[Libro]:
        """Retorna todos los libros registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Libro]:
        """Retorna un libro por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    @auditar("Actualizar libro")
    def actualizar(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
    ) -> Libro:
        """Actualiza los datos de un libro existente.

        Args:
            id (int): Identificador del libro a modificar.
            isbn (str): Nuevo ISBN del libro.
            titulo (str): Nuevo título.
            autor (str): Nuevo autor.
            editorial_id (int): Nuevo ID de editorial.
            genero_id (int): Nuevo ID de género.

        Returns:
            Libro: El libro actualizado.

        Raises:
            ValueError: Si no existe el libro, si el ISBN está duplicado,
                        o si la editorial/género no existen.
        """
        libro = self._repo.leer_por_id(id)
        if libro is None:
            raise ValueError(f"No existe un libro con id {id}.")
        libro.isbn = isbn
        libro.titulo = titulo
        libro.autor = autor
        libro.editorial_id = editorial_id
        libro.genero_id = genero_id
        duplicado_isbn = any(
            otro.isbn == libro.isbn and otro.id != id
            for otro in self._repo.leer_todos()
        )
        if duplicado_isbn:
            raise ValueError(f"Ya existe un libro con el ISBN '{libro.isbn}'.")
        if self._repo_editorial.leer_por_id(editorial_id) is None:
            raise ValueError(f"No existe una editorial con id {editorial_id}.")
        if self._repo_genero.leer_por_id(genero_id) is None:
            raise ValueError(f"No existe un género con id {genero_id}.")
        return self._repo.actualizar(libro)

    @auditar("Eliminar libro")
    def eliminar(self, id: int) -> bool:
        """Elimina un libro por su id, junto con sus resultados de scraping.

        Args:
            id (int): Identificador del libro a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.

        Raises:
            ValueError: Si el libro tiene precios o stock asociados.
        """
        precios = self._repo_precio.leer_todos()
        if any(precio.libro_id == id for precio in precios):
            raise ValueError(
                "No se puede eliminar: tiene precios asociados."
            )
        if self._repo_stock.leer_por_libro(id) is not None:
            raise ValueError(
                "No se puede eliminar: tiene stock registrado."
            )
        self._repo_precio_web.eliminar_por_libro(id)
        return self._repo.eliminar(id)


class ServicioPrecio:
    """Lógica de negocio para la entidad Precio."""

    def __init__(
        self,
        repositorio: IRepositorio[Precio],
        repo_libro: IRepositorio[Libro],
        repo_moneda: IRepositorio[Moneda],
    ) -> None:
        self._repo = repositorio
        self._repo_libro = repo_libro
        self._repo_moneda = repo_moneda

    def siguiente_id(self) -> int:
        """Retorna el próximo id disponible (el mayor existente más 1)."""
        return max((p.id for p in self._repo.leer_todos()), default=0) + 1

    @auditar("Crear precio")
    def crear(
        self, id: int, libro_id: int, moneda_id: int, valor: float
    ) -> Precio:
        """Crea un precio para un libro en una moneda dada.

        Args:
            id (int): Identificador único del precio.
            libro_id (int): ID del libro al que pertenece el precio.
            moneda_id (int): ID de la moneda en que se expresa el precio.
            valor (float): Valor del precio (debe ser mayor a 0).

        Returns:
            Precio: El precio creado.

        Raises:
            ValueError: Si ya existe un precio para esa combinación
                        libro+moneda, o si el libro/moneda no existen.
        """
        if self._repo_libro.leer_por_id(libro_id) is None:
            raise ValueError(f"No existe un libro con id {libro_id}.")
        if self._repo_moneda.leer_por_id(moneda_id) is None:
            raise ValueError(f"No existe una moneda con id {moneda_id}.")
        duplicado = any(
            p.libro_id == libro_id and p.moneda_id == moneda_id
            for p in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe un precio para el libro {libro_id} "
                f"en la moneda {moneda_id}."
            )
        return self._repo.crear(Precio(id, libro_id, moneda_id, valor))

    def obtener_todos(self) -> List[Precio]:
        """Retorna todos los precios registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Precio]:
        """Retorna un precio por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def obtener_por_libro(self, libro_id: int) -> List[Precio]:
        """Retorna todos los precios asociados a un libro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            List[Precio]: Lista de precios del libro en distintas monedas.
        """
        return [p for p in self._repo.leer_todos() if p.libro_id == libro_id]

    @auditar("Actualizar precio")
    def actualizar(
        self, id: int, libro_id: int, moneda_id: int, valor: float
    ) -> Precio:
        """Actualiza los datos de un precio existente.

        Args:
            id (int): Identificador del precio a modificar.
            libro_id (int): Nuevo ID de libro.
            moneda_id (int): Nuevo ID de moneda.
            valor (float): Nuevo valor del precio.

        Returns:
            Precio: El precio actualizado.

        Raises:
            ValueError: Si no existe el precio, si el libro/moneda no existen,
                        o si la combinación libro+moneda ya está en uso por
                        otro precio.
        """
        precio = self._repo.leer_por_id(id)
        if precio is None:
            raise ValueError(f"No existe un precio con id {id}.")
        if self._repo_libro.leer_por_id(libro_id) is None:
            raise ValueError(f"No existe un libro con id {libro_id}.")
        if self._repo_moneda.leer_por_id(moneda_id) is None:
            raise ValueError(f"No existe una moneda con id {moneda_id}.")
        duplicado = any(
            p.libro_id == libro_id and p.moneda_id == moneda_id and p.id != id
            for p in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe un precio para el libro {libro_id} "
                f"en la moneda {moneda_id}."
            )
        precio.libro_id = libro_id
        precio.moneda_id = moneda_id
        precio.valor = valor
        return self._repo.actualizar(precio)

    @auditar("Eliminar precio")
    def eliminar(self, id: int) -> bool:
        """Elimina un precio por su id.

        Args:
            id (int): Identificador del precio a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioStock:
    """Lógica de negocio para la entidad Stock."""

    def __init__(
        self,
        repositorio: IRepositorioStock,
        repo_libro: IRepositorio[Libro],
    ) -> None:
        self._repo = repositorio
        self._repo_libro = repo_libro

    @auditar("Crear stock")
    def crear(self, libro_id: int, cantidad: int) -> Stock:
        """Crea un registro de stock para un libro.

        Args:
            libro_id (int): ID del libro.
            cantidad (int): Cantidad inicial en stock (debe ser >= 0).

        Returns:
            Stock: El registro de stock creado.

        Raises:
            ValueError: Si no existe el libro, o si ya tiene stock registrado.
        """
        if self._repo_libro.leer_por_id(libro_id) is None:
            raise ValueError(f"No existe un libro con id {libro_id}.")
        return self._repo.crear(Stock(libro_id, cantidad))

    def obtener_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Retorna el stock de un libro, o None si no existe registro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            Optional[Stock]: El stock del libro, o None.
        """
        return self._repo.leer_por_libro(libro_id)

    def obtener_todos(self) -> List[Stock]:
        """Retorna el stock de todos los libros."""
        return self._repo.leer_todos()

    @auditar("Actualizar stock")
    def actualizar(self, libro_id: int, cantidad: int) -> Stock:
        """Actualiza la cantidad en stock de un libro.

        Args:
            libro_id (int): ID del libro.
            cantidad (int): Nueva cantidad en stock (debe ser >= 0).

        Returns:
            Stock: El stock actualizado.

        Raises:
            ValueError: Si no existe stock para ese libro.
        """
        stock = self._repo.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError(
                f"No existe stock registrado para el libro {libro_id}."
            )
        stock.cantidad = cantidad
        return self._repo.actualizar(stock)

    @auditar("Eliminar stock")
    def eliminar(self, libro_id: int) -> bool:
        """Elimina el registro de stock de un libro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(libro_id)


class ServicioCotizacionDolar:
    """Lógica de negocio para la entidad CotizacionDolar."""

    def __init__(
        self,
        repositorio: IRepositorioCotizacionDolar,
        repo_tipo: IRepositorio[TipoCotizacion],
    ) -> None:
        self._repo = repositorio
        self._repo_tipo = repo_tipo

    @auditar("Crear cotización")
    def crear(
        self, tipo_id: int, fecha: date, valor: float
    ) -> CotizacionDolar:
        """Registra una nueva cotización del dólar para un tipo y fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (date): Fecha de la cotización.
            valor (float): Valor del dólar en esa fecha (debe ser > 0).

        Returns:
            CotizacionDolar: La cotización creada.

        Raises:
            ValueError: Si el tipo no existe, o si ya hay una cotización para
                        ese tipo y fecha.
        """
        if self._repo_tipo.leer_por_id(tipo_id) is None:
            raise ValueError(
                f"No existe un tipo de cotización con id {tipo_id}."
            )
        return self._repo.crear(CotizacionDolar(tipo_id, fecha, valor))

    def obtener_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        """Retorna la cotización de un tipo en una fecha específica.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (date): Fecha de consulta.

        Returns:
            Optional[CotizacionDolar]: La cotización, o None si no existe.
        """
        return self._repo.leer_por_tipo_y_fecha(tipo_id, fecha)

    def obtener_historico_por_tipo(
        self, tipo_id: int
    ) -> List[CotizacionDolar]:
        """Retorna el historial de cotizaciones de un tipo, ordenado por fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Lista de cotizaciones históricas ordenadas
            por fecha.
        """
        return self._repo.leer_historico_por_tipo(tipo_id)

    def obtener_ultima_cotizacion(
        self, tipo_id: int
    ) -> Optional[CotizacionDolar]:
        """Retorna la cotización más reciente disponible para un tipo.

        Args:
            tipo_id (int): ID del tipo de cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización más reciente, o None si
            no hay registros.
        """
        historico = self._repo.leer_historico_por_tipo(tipo_id)
        return historico[-1] if historico else None

    @auditar("Obtener cotizaciones por API")
    def obtener_cotizaciones(self) -> List[CotizacionDolar]:
        """Busca, descarga y registra las cotizaciones del dólar desde la API.

        Lee la URL de la API desde la variable de entorno API_URL, descarga
        las cotizaciones vigentes y las registra en la base de datos a través
        del repositorio. Si el tipo de cotización no existe, lo crea. Si ya
        existe una cotización para el tipo y fecha, actualiza su valor.

        Returns:
            List[CotizacionDolar]: Lista de cotizaciones registradas o
            actualizadas.

        Raises:
            ValueError: Si falta la variable de entorno API_URL.
            requests.RequestException: Si ocurre un error al consultar la API.
        """
        load_dotenv()
        url = os.getenv("API_URL")
        if not url:
            raise ValueError("Falta la variable de entorno API_URL.")

        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        items = respuesta.json()

        cotizaciones: List[CotizacionDolar] = []
        for item in items:
            nombre = item["nombre"].strip()
            tipos = self._repo_tipo.leer_todos()
            tipo = next(
                (t for t in tipos if t.nombre.lower() == nombre.lower()),
                None,
            )
            if tipo is None:
                nuevo_id = max((t.id for t in tipos), default=0) + 1
                tipo = self._repo_tipo.crear(TipoCotizacion(nuevo_id, nombre))

            fecha = date.fromisoformat(item["fechaActualizacion"][:10])
            valor = float(item["venta"])

            existente = self._repo.leer_por_tipo_y_fecha(tipo.id, fecha)
            if existente is not None:
                existente.valor = valor
                cotizacion = self._repo.actualizar(existente)
            else:
                cotizacion = self._repo.crear(
                    CotizacionDolar(tipo.id, fecha, valor)
                )

            cotizaciones.append(cotizacion)

        return cotizaciones

    @auditar("Actualizar cotización")
    def actualizar(
        self, tipo_id: int, fecha: date, valor: float
    ) -> CotizacionDolar:
        """Actualiza el valor de una cotización existente.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (date): Fecha de la cotización a modificar.
            valor (float): Nuevo valor de la cotización.

        Returns:
            CotizacionDolar: La cotización actualizada.

        Raises:
            ValueError: Si no existe la cotización para ese tipo y fecha.
        """
        cotizacion = self._repo.leer_por_tipo_y_fecha(tipo_id, fecha)
        if cotizacion is None:
            raise ValueError(
                f"No existe cotización para el tipo {tipo_id} "
                f"en la fecha {fecha}."
            )
        cotizacion.valor = valor
        return self._repo.actualizar(cotizacion)

    @auditar("Eliminar cotización")
    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (date): Fecha de la cotización a eliminar.

        Returns:
            bool: True si fue eliminada, False si no existía.
        """
        return self._repo.eliminar(tipo_id, fecha)


@dataclass
class Servicios:
    """Contenedor con todas las instancias de los servicios del sistema."""

    generos: ServicioGenero
    editoriales: ServicioEditorial
    monedas: ServicioMoneda
    tipos: ServicioTipoCotizacion
    libros: ServicioLibro
    precios: ServicioPrecio
    stock: ServicioStock
    cotizaciones: ServicioCotizacionDolar
    precios_web: ServicioPrecioWeb
    auditoria: ServicioAuditoria
