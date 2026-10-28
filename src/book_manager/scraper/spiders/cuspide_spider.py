"""Spider que obtiene de Cúspide los precios de los libros del catálogo."""
from datetime import datetime
from typing import Any, AsyncIterator, Iterator, List
from urllib.parse import urlencode

from scrapy import Request, Spider
from scrapy.http import Response

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import Libro
from book_manager.repositories.repositories import RepositorioLibro
from book_manager.scraper.items import LibroWebItem
from book_manager.scraper.loaders import LibroWebLoader


class CuspideSpider(Spider):
    """Busca cada título del catálogo en Cúspide y extrae sus fichas.

    Solo se buscan los libros del catálogo y, de cada búsqueda, se toman
    los primeros MAX_RESULTADOS resultados.
    """

    name = "cuspide"
    allowed_domains = ["cuspide.com"]
    URL_BUSQUEDA = "https://cuspide.com/?"
    MAX_RESULTADOS = 10

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Todas las fichas de una ejecución comparten la fecha de extracción.
        self.fecha_extraccion = datetime.now()

    def _libros(self) -> List[Libro]:
        """Retorna los libros del catálogo guardados en la base de datos."""
        conexion = ConexionDB()
        try:
            return RepositorioLibro(conexion).leer_todos()
        finally:
            conexion.cerrar()

    async def start(self) -> AsyncIterator[Request]:
        """Genera una búsqueda en Cúspide por cada libro del catálogo."""
        libros = self._libros()
        if not libros:
            self.logger.warning(
                "No hay libros en el catálogo: cargue los datos antes."
            )
            return
        for libro in libros:
            parametros = urlencode({"s": libro.titulo, "post_type": "product"})
            yield Request(
                self.URL_BUSQUEDA + parametros,
                callback=self.parse_busqueda,
                cb_kwargs={"libro_id": libro.id},
            )

    def parse_busqueda(
        self, response: Response, libro_id: int
    ) -> Iterator[Request]:
        """Sigue los primeros resultados de la búsqueda de un libro.

        Args:
            response (Response): Página de resultados de la búsqueda.
            libro_id (int): Id del libro del catálogo que se buscó.
        """
        enlaces = response.css(
            "div.products div.product-small.col .product-title a::attr(href)"
        ).getall()[: self.MAX_RESULTADOS]
        if not enlaces:
            self.logger.info("Sin resultados para el libro %s", libro_id)
        for posicion, enlace in enumerate(enlaces, 1):
            # dont_filter: la misma ficha puede aparecer en varias búsquedas.
            yield response.follow(
                enlace,
                callback=self.parse_libro,
                cb_kwargs={"libro_id": libro_id, "posicion": posicion},
                dont_filter=True,
            )

    def parse_libro(
        self, response: Response, libro_id: int, posicion: int
    ) -> Iterator[LibroWebItem]:
        """Extrae los datos de la ficha de un libro.

        Args:
            response (Response): Ficha del libro en Cúspide.
            libro_id (int): Id del libro del catálogo que se buscó.
            posicion (int): Posición de la ficha en los resultados.
        """
        loader = LibroWebLoader(response=response)
        loader.add_value("libro_id", libro_id)
        loader.add_value("posicion", posicion)
        loader.add_value("url", response.url)
        loader.add_value("fecha_extraccion", self.fecha_extraccion)
        loader.add_css("titulo", "h1.product-title::text")
        loader.add_css("isbn", ".product_meta .sku::text")
        # Si el libro está en oferta, el precio vigente está dentro de <ins>.
        loader.add_css("precio", "p.product-page-price ins bdi::text")
        loader.add_css("precio", "p.product-page-price bdi::text")
        loader.add_xpath(
            "precio_usd",
            "//span[starts-with(normalize-space(text()), 'U$s')]/span/text()",
        )
        loader.add_css(
            "imagen_url", ".woocommerce-product-gallery__image a::attr(href)"
        )
        loader.add_css("formas_pago", "#contentPaymentsPopUpArg li::text")
        loader.add_css("descripcion", "p.livriz-text-synopsis::text")
        for fila in response.css("table.woocommerce-product-attributes tr"):
            etiqueta = fila.css("th::text").get(default="").strip()
            valor = " ".join(fila.css("td ::text").getall()).strip()
            if etiqueta and valor:
                loader.add_value("especificaciones", f"{etiqueta}: {valor}")
        yield loader.load_item()
