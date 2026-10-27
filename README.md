# Book Manager

## Sprint 3

### Objetivo

Aplicar los conocimientos adquiridos en programación orientada a objetos y persistencia de datos, incorporando la obtención de datos desde la web (web scraping), la generación de reportes y la auditoría de las operaciones del sistema.

### Introducción y contexto

Una librería con venta al público necesita modernizar su sistema de gestión de inventario de libros. Debido a la fluctuación en los costos de importación, el sistema gestiona precios en distintas monedas y sigue la cotización del dólar para actualizar sus valores.

En este sprint se obtienen datos de la web para trabajar con ellos: con un scraper hecho con Scrapy se consultan los precios de un competidor con venta online (Cúspide) para los libros de nuestro catálogo. Con esos datos se generan alertas por diferencias de precio y reportes en Excel, y todas las operaciones del sistema quedan registradas en una tabla de auditoría.
