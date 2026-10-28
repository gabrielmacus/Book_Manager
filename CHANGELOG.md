## Sprint 3

[Correcciones]
- Datos de ejemplo con los ISBN reales de las ediciones que vende Cúspide (preload_data y migrations/sql/05_libros.sql), para que la comparación encuentre el libro correcto.
- Sin ISBN coincidente, la comparación solo acepta títulos casi idénticos (similitud mínima 0.9).
- El scraping avisa con un error si el catálogo está vacío o si no obtuvo resultados, en lugar de generar alertas con datos de una ejecución anterior.
- El scraper también toma la ficha cuando Cúspide redirige directamente a ella (búsquedas con un único resultado).
- Al eliminar un libro se borran también sus resultados de scraping (precios_web).
- La auditoría registra también las consultas: listados, búsquedas, cotizaciones, lista bimonetaria, exportación de precios a CSV e historial de auditoría.
- La consola muestra la ruta del archivo de alertas y del reporte; la fecha de extracción se guarda sin microsegundos en el CSV.
- Las fechas de auditoría y de extracción se guardan en UTC y se muestran en hora de Argentina (historial, CSV, Excel y nombres de archivo), así coinciden se ejecute en Colab o en una PC.
- En Colab, los enlaces para descargar las alertas y los reportes se muestran al salir del programa (opción 0): files.download o un enlace mostrado mientras el menú espera un input dejaban la consola trabada.
- Type hints en el decorador auditar, docstrings faltantes y correcciones de estilo PEP8.

[Ejercicio 07]
- Nuevas opciones del menú principal: 12. Ejecutar Scraping de Precios (pide la diferencia en % antes de cada ejecución y genera las alertas), 13. Generar Reporte Excel y 14. Ver Historial de Auditoría.
- En Colab, las alertas y el reporte se descargan en el navegador; fuera de Colab se informa la ruta del archivo.

[Ejercicio 06]
- Auditoría: entidad Auditoria, tabla auditoria (AuditoriaModel), RepositorioAuditoria y ServicioAuditoria. Registra acción, fecha y detalles.
- Decorador auditar(accion): registra cada alta, modificación y baja de los servicios, la obtención de cotizaciones por API, el scraping y el reporte Excel, indicando si la operación terminó bien o con error.
- main configura la auditoría y la agrega al contenedor Servicios.

[Ejercicio 05]
- ServicioPrecioWeb.generar_reporte_excel: genera reportes/reporte_<fecha_hora>.xlsx con pandas, con las columnas Libro, Precio interno, Precio web, Diferencia y Fecha de extracción de la última ejecución del scraper.

[Ejercicio 04]
- ServicioPrecioWeb compara precios internos en pesos con la última extracción web, convirtiendo precios en USD con el dólar oficial.
- Elige el resultado web por ISBN o por similitud de título y genera reportes/alertas_<fecha_hora>.csv según el umbral indicado.
- Ejecuta Scrapy en un proceso aparte y avisa cuando el catálogo está vacío.

[Ejercicio 03]
- Scraper CuspideSpider con Scrapy: busca en Cúspide cada título del catálogo y recorre los primeros 10 resultados de cada búsqueda.
- De cada ficha obtiene precio en pesos y en dólares, URL de la imagen, formas de pago, descripción (sinopsis) y especificaciones, además del ISBN y la fecha de extracción.
- Item LibroWebItem y loader LibroWebLoader, que limpian espacios, convierten los precios ('$ 48.500,00' a 48500.0) y unen las listas.
- Pipelines: ValidarLibroPipeline descarta fichas sin título, URL o precio y GuardarPrecioWebPipeline guarda cada ficha en la base.
- Nueva entidad PrecioWeb, tabla precios_web (PrecioWebModel) y RepositorioPrecioWeb.
- La carga y la migración de datos borran primero los precios web, que dependen de los libros.
- Configuración del proyecto (settings.py): respeta robots.txt y espacia los pedidos al sitio. Se requiere scrapy>=2.13.

[Ejercicio 02]
- Función cargar_desde_sql en migrations.py: crea las tablas, borra los datos previos y ejecuta en orden los archivos .sql de migrations/sql dentro de una única transacción.
- main(import_default_data=True) carga los datos de ejemplo desde los archivos .sql.

[Ejercicio 01]
- Creación de la rama Sprint_3 a partir de Sprint_2.
- Nueva estructura de directorios: scraper (proyecto Scrapy con scrapy.cfg, settings, items, pipelines y spiders) y reportes.
- Dependencias en requirements.txt: scrapy, pandas y openpyxl.
- Los repositorios de base de datos pasan a llamarse RepositorioGenero, RepositorioLibro, etc. (sin el sufijo DB).
- .gitignore: se ignoran los reportes Excel generados (*.xlsx).
- README actualizado al Sprint 3.

## Sprint 2

[Ejercicio 08]
- Nuevas opciones del menú principal: 9. Obtener cotizaciones por API, 10. Lista de precios bimonetaria y 11. Exportar precios a CSV.
- La lista bimonetaria muestra cada libro en ARS y en la moneda elegida; convierte entre ARS y USD con la última cotización del tipo seleccionado.
- La exportación genera exports/precios.csv con una columna por cada moneda.
- Corrección (TP1, Ejercicio 05): generar_csvs carga las entidades de ejemplo a través de los repositorios CSV en lugar de escribir los archivos con csv.writer.
- Archivos .sql generados por la migración agregados a migrations/sql.
- Correcciones de estilo PEP8: indentación de migrations.py, líneas largas, nombres ambiguos, imports sin uso y eliminación del ajuste de sys.path en main.py.
- Dependencia psycopg[binary] en requirements.txt: SQLAlchemy 2.1 usa psycopg (versión 3) como driver por defecto de PostgreSQL.
- Corrección: en notebooks la consola ya no borra la salida (imprime un separador), para que quede registro de las operaciones y Colab muestre siempre el input.

[Ejercicio 07]
- Implementación de obtener_cotizaciones() en ServicioCotizacionDolar: lee API_URL del .env con python-dotenv, descarga las cotizaciones de dolarapi, crea los tipos de cotización que no existen y da de alta o actualiza cada cotización.

[Ejercicio 06]
- Repositorios con base de datos (RepositorioGeneroDB, RepositorioEditorialDB, RepositorioMonedaDB, RepositorioTipoCotizacionDB, RepositorioLibroDB, RepositorioPrecioDB, RepositorioStockDB y RepositorioCotizacionDolarDB) que convierten entre modelos y entidades.
- Corrección (TP1, Ejercicio 07): el armado de repositorios y servicios pasa a main.py; ConsoleUI recibe el contenedor Servicios.
- main crea las tablas y, con import_default_data=True, genera los CSV y migra los datos a la base.

[Ejercicio 05]
- migrar_datos lee los CSV del Sprint 1 con los repositorios CSV, carga la base en una transacción y genera un archivo .sql por tabla en migrations/sql.
- La migración borra los datos previos para poder ejecutarse más de una vez sin duplicar.

[Ejercicio 04]
- Creación de las tablas del sistema en models.py con sus tipos de datos, claves foráneas y relaciones (relationship).
- Función crear_tablas para crear las tablas en la base.

[Ejercicio 03]
- Context manager transaccion() en ConexionDB: hace commit si el bloque termina bien, rollback si falla y siempre cierra la sesión.
- Corrección: la consola usa clear_output(wait=True) para que Colab no salte de celda al elegir una opción.

[Ejercicio 02]
- Creación de la clase ConexionDB en database/connection.py con SQLAlchemy.
- Lee DATABASE_URL del entorno, de .env o de .env.local (sin pisar variables ya definidas).
- Expone el engine, nueva_sesion() para obtener una Session y cerrar() para liberar conexiones.

[Ejercicio 01]
- Creación de la rama Sprint_2 a partir de Sprint_1.
- Nueva estructura de directorios: database/connection.py, models/models.py, migrations/migrations.py y migrations/sql.
- Dependencias en requirements.txt: sqlalchemy, psycopg2-binary, python-dotenv y requests.
- README actualizado al Sprint 2.
- Archivo .env con API_URL; DATABASE_URL va en .env.local (ignorado por git) o como secret de Colab.

## Sprint 1

[Ejercicio 07]
- Creación del archivo main.py con la función main(import_default_data), que ejecuta ConsoleUI.
- Con import_default_data=True genera los CSV de importación con generar_csvs antes de iniciar; con False usa los datos existentes.

[Ejercicio 06]
- Creación de la interfaz de consola en ui/console.py (ConsoleUI) con menú principal y submenús por entidad.
- Crear, listar, buscar, actualizar y eliminar para las 8 clases, a través de los servicios.
- Los ids de alta se asignan con siguiente_id() y los errores de los servicios se muestran por consola.
- Consultas adicionales: precios de un libro, histórico y última cotización de un tipo.
- Adaptación de la clase Servicios a los constructores actuales de los servicios.

[Ejercicio 05]
- Creación de preload_data.py, que genera los archivos CSV de importación en migrations/csv.
- Un archivo CSV por entidad (géneros, editoriales, monedas, tipos de cotización, libros, precios, stock y cotizaciones), con al menos 10 registros cada uno.
- Los CSV tienen el formato que usan los repositorios; generar_csvs no pisa los archivos existentes salvo que se indique.

[Ejercicio 04]
- Implementación de ServicioGenero, ServicioEditorial, ServicioMoneda y ServicioTipoCotizacion con validación de nombres/códigos únicos.
- Implementación de ServicioLibro con validación de ISBN único e integridad referencial (editorial y género).
- Implementación de ServicioPrecio con validación de combinación única libro+moneda.
- Implementación de ServicioStock con control de cantidad no negativa y validación de existencia del libro.
- Implementación de ServicioCotizacionDolar con historial y obtención de la última cotización disponible.

[Ejercicio 03]
- Definición de las interfaces IRepositorio, IRepositorioStock e IRepositorioCotizacionDolar en repositories.py.
- Implementación de repositorios que persisten a CSV: RepositorioGeneroCsv, RepositorioEditorialCsv, RepositorioMonedaCsv, RepositorioTipoCotizacionCsv, RepositorioLibroCsv, RepositorioPrecioCsv, RepositorioStockCsv y RepositorioCotizacionDolarCsv.
- Lógica común de lectura y escritura del CSV en _RepositorioCsvBase.

[Ejercicio 02]
- Definición de las entidades en entities.py: EntidadBase, Genero, Editorial, Moneda, TipoCotizacion, Libro, Precio, Stock y CotizacionDolar.
- Encapsulación de atributos con propiedades y validaciones.
- Relaciones entre entidades mediante ids.

[Ejercicio 01]
- Inicialización del repositorio y creación de la rama Sprint_1.
- Creación de la estructura de directorios del proyecto.
- Agregado de README.md, CHANGELOG.md, requirements.txt y .gitignore.
