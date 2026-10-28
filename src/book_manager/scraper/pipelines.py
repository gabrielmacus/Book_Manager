"""Pipelines del scraper de Cúspide: validación y guardado en la base."""
from typing import Any, Optional

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import PrecioWeb
from book_manager.models.models import crear_tablas
from book_manager.repositories.repositories import RepositorioPrecioWeb


class ValidarLibroPipeline:
    """Descarta las fichas sin título, URL o precio."""

    def process_item(self, item: Any, spider: Optional[Any] = None) -> Any:
        """Descarta el item si le falta título, URL o precio."""
        adapter = ItemAdapter(item)
        for campo in ("titulo", "url", "precio"):
            if not adapter.get(campo):
                raise DropItem(f"Ficha sin {campo}: {adapter.get('url')}")
        return item


class GuardarPrecioWebPipeline:
    """Guarda cada ficha válida en la tabla precios_web."""

    def open_spider(self, spider: Optional[Any] = None) -> None:
        """Abre la conexión a la base al iniciar el spider."""
        self._conexion = ConexionDB()
        crear_tablas(self._conexion)  # por si precios_web aún no existe
        self._repositorio = RepositorioPrecioWeb(self._conexion)

    def close_spider(self, spider: Optional[Any] = None) -> None:
        """Cierra la conexión a la base al terminar el spider."""
        self._conexion.cerrar()

    def process_item(self, item: Any, spider: Optional[Any] = None) -> Any:
        """Guarda el item como un registro de PrecioWeb."""
        adapter = ItemAdapter(item)
        self._repositorio.crear(
            PrecioWeb(
                adapter["libro_id"],
                adapter["posicion"],
                adapter["titulo"],
                adapter["url"],
                adapter["precio"],
                adapter["fecha_extraccion"],
                precio_usd=adapter.get("precio_usd"),
                isbn=adapter.get("isbn"),
                imagen_url=adapter.get("imagen_url"),
                formas_pago=adapter.get("formas_pago", ""),
                descripcion=adapter.get("descripcion", ""),
                especificaciones=adapter.get("especificaciones", ""),
            )
        )
        return item
