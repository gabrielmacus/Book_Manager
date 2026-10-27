"""Items del scraper de Cúspide."""
import scrapy


class LibroWebItem(scrapy.Item):
    """Datos de un libro obtenidos de una ficha de Cúspide."""

    libro_id = scrapy.Field()
    posicion = scrapy.Field()
    titulo = scrapy.Field()
    url = scrapy.Field()
    isbn = scrapy.Field()
    precio = scrapy.Field()
    precio_usd = scrapy.Field()
    imagen_url = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    especificaciones = scrapy.Field()
    fecha_extraccion = scrapy.Field()
