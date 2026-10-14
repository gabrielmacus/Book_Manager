# Book Manager

## Sprint 2

### Objetivo

Aplicar los conocimientos adquiridos en programación orientada a objetos y almacenamiento de datos para su persistencia, consolidando las bases de manejo de bases de datos, normalización, conexión segura y carga inicial.

### Introducción y contexto

Una librería con venta al público necesita modernizar su sistema de gestión de inventario de libros. Debido a la fluctuación en los costos de importación, el sistema gestiona precios en distintas monedas y sigue la cotización del dólar para actualizar sus valores.

En este sprint la aplicación pasa a persistir en una base de datos relacional (PostgreSQL en Supabase) mediante el ORM SQLAlchemy. Se migran a tablas relacionales los datos cargados en los archivos CSV del Sprint 1 y se consultan las cotizaciones del dólar desde una API externa.
