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
