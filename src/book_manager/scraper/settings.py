"""Configuración del proyecto Scrapy de Book Manager."""

BOT_NAME = "book_manager"

SPIDER_MODULES = ["book_manager.scraper.spiders"]
NEWSPIDER_MODULE = "book_manager.scraper.spiders"

# Navegación respetuosa con el sitio: respeta robots.txt y espacia pedidos.
USER_AGENT = "BookManager/1.0 (TP Seminario de Actualizacion)"
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 0.5

ITEM_PIPELINES = {
    "book_manager.scraper.pipelines.ValidarLibroPipeline": 100,
    "book_manager.scraper.pipelines.GuardarPrecioWebPipeline": 300,
}

# La consola no necesita control remoto del crawler (telnet ni HTTP).
TELNETCONSOLE_ENABLED = False
REMOTE_CONTROL_ENABLED = False

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
