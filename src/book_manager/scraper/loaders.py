"""Loaders del scraper de Cúspide: limpian los datos de cada ficha."""
import re
from typing import Any, Optional

from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader

from book_manager.scraper.items import LibroWebItem


def normalizar_espacios(valor: Any) -> Any:
    """Reemplaza espacios repetidos (incluido &nbsp;) por uno solo.

    Los valores que no son texto (ids, fechas) se devuelven sin cambios.
    """
    return " ".join(valor.split()) if isinstance(valor, str) else valor


def convertir_precio(texto: str) -> Optional[float]:
    """Convierte un precio con formato argentino a número.

    Args:
        texto (str): Precio como texto, por ejemplo '$ 48.500,00' o '31,09'.

    Returns:
        Optional[float]: El precio (48500.0), o None si no hay número.
    """
    numero = re.sub(r"[^\d,]", "", texto).replace(",", ".")
    return float(numero) if numero else None


def quitar_prefijo(texto: str) -> str:
    """Quita el '>' inicial con el que Cúspide lista las formas de pago."""
    return texto.lstrip("> ").strip()


class LibroWebLoader(ItemLoader):
    """Loader de LibroWebItem: limpia espacios, precios y listas."""

    default_item_class = LibroWebItem
    default_input_processor = MapCompose(normalizar_espacios)
    default_output_processor = TakeFirst()

    precio_in = MapCompose(normalizar_espacios, convertir_precio)
    precio_usd_in = MapCompose(normalizar_espacios, convertir_precio)
    formas_pago_in = MapCompose(normalizar_espacios, quitar_prefijo)
    formas_pago_out = Join("; ")
    descripcion_out = Join(" ")
    especificaciones_out = Join("; ")
