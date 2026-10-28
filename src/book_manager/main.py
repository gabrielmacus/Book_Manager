from book_manager.database.connection import ConexionDB
from book_manager.migrations.migrations import cargar_desde_sql
from book_manager.models.models import crear_tablas
from book_manager.preload_data.preload_data import CSV_DIR
from book_manager.repositories.repositories import (
    RepositorioAuditoria,
    RepositorioCotizacionDolar,
    RepositorioEditorial,
    RepositorioGenero,
    RepositorioLibro,
    RepositorioMoneda,
    RepositorioPrecio,
    RepositorioPrecioWeb,
    RepositorioStock,
    RepositorioTipoCotizacion,
)
from book_manager.services.services import (
    ServicioAuditoria,
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioPrecioWeb,
    ServicioStock,
    ServicioTipoCotizacion,
    Servicios,
    configurar_auditoria,
)
from book_manager.ui.console import ConsoleUI


def main(import_default_data: bool = False) -> None:
    """Punto de entrada principal del sistema Book Manager.

    Args:
        import_default_data (bool): Si es True, carga en la base de datos
            los datos de ejemplo desde los archivos sql antes de iniciar.
    """
    conexion = ConexionDB()
    crear_tablas(conexion)

    if import_default_data:
        cargar_desde_sql(str(CSV_DIR.parent / "sql"))

    repo_genero = RepositorioGenero(conexion)
    repo_editorial = RepositorioEditorial(conexion)
    repo_moneda = RepositorioMoneda(conexion)
    repo_tipo = RepositorioTipoCotizacion(conexion)
    repo_libro = RepositorioLibro(conexion)
    repo_precio = RepositorioPrecio(conexion)
    repo_stock = RepositorioStock(conexion)
    repo_cotizacion = RepositorioCotizacionDolar(conexion)
    repo_precio_web = RepositorioPrecioWeb(conexion)
    repo_auditoria = RepositorioAuditoria(conexion)

    servicio_auditoria = ServicioAuditoria(repo_auditoria)
    configurar_auditoria(servicio_auditoria)

    servicios = Servicios(
        generos=ServicioGenero(repo_genero, repo_libro),
        editoriales=ServicioEditorial(repo_editorial, repo_libro),
        monedas=ServicioMoneda(repo_moneda, repo_precio),
        tipos=ServicioTipoCotizacion(repo_tipo, repo_cotizacion),
        libros=ServicioLibro(
            repo_libro,
            repo_editorial,
            repo_genero,
            repo_precio,
            repo_stock,
            repo_precio_web,
        ),
        precios=ServicioPrecio(repo_precio, repo_libro, repo_moneda),
        stock=ServicioStock(repo_stock, repo_libro),
        cotizaciones=ServicioCotizacionDolar(repo_cotizacion, repo_tipo),
        precios_web=ServicioPrecioWeb(
            repo_precio_web,
            repo_libro,
            repo_precio,
            repo_moneda,
            repo_cotizacion,
            repo_tipo,
        ),
        auditoria=servicio_auditoria,
    )

    ConsoleUI(servicios).run()


if __name__ == "__main__":
    main()
