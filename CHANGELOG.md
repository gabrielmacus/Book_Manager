[Ejercicio 06]
-Creación de la interfaz gráfica.
-Creación del menú principal con género, editoriales, libros, etc.
-Permite realizar las funciones de crear registro nuevo, ver el listado, modificar un listado y eliminarlo.

[Ejercicio 05]
- Creación de archivos para carga de datos.
- Se importan las entidades libro, género, etc.
- Se crea un archivo CSV con las entidades.

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
