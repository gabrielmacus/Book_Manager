from book_manager.database.connection import ConexionDB
from book_manager.migrations.migrations import migrar_datos
from book_manager.models.models import crear_tablas
from book_manager.preload_data.preload_data import CSV_DIR, generar_csvs
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolarDB,
    RepositorioEditorialDB,
    RepositorioGeneroDB,
    RepositorioLibroDB,
    RepositorioMonedaDB,
    RepositorioPrecioDB,
    RepositorioStockDB,
    RepositorioTipoCotizacionDB,
)
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
    Servicios,
)
from book_manager.ui.console import ConsoleUI


def main(import_default_data: bool = False) -> None:
    """Punto de entrada principal del sistema Book Manager.

    Args:
        import_default_data (bool): Si es True, genera los archivos CSV de
            ejemplo y migra sus datos a la base de datos antes de iniciar.
    """
    conexion = ConexionDB()
    crear_tablas(conexion)

    if import_default_data:
        generar_csvs(sobrescribir=True)
        migrar_datos(str(CSV_DIR), str(CSV_DIR.parent / "sql"))

    repo_genero = RepositorioGeneroDB(conexion)
    repo_editorial = RepositorioEditorialDB(conexion)
    repo_moneda = RepositorioMonedaDB(conexion)
    repo_tipo = RepositorioTipoCotizacionDB(conexion)
    repo_libro = RepositorioLibroDB(conexion)
    repo_precio = RepositorioPrecioDB(conexion)
    repo_stock = RepositorioStockDB(conexion)
    repo_cotizacion = RepositorioCotizacionDolarDB(conexion)

    servicios = Servicios(
        generos=ServicioGenero(repo_genero, repo_libro),
        editoriales=ServicioEditorial(repo_editorial, repo_libro),
        monedas=ServicioMoneda(repo_moneda, repo_precio),
        tipos=ServicioTipoCotizacion(repo_tipo, repo_cotizacion),
        libros=ServicioLibro(
            repo_libro, repo_editorial, repo_genero, repo_precio, repo_stock
        ),
        precios=ServicioPrecio(repo_precio, repo_libro, repo_moneda),
        stock=ServicioStock(repo_stock, repo_libro),
        cotizaciones=ServicioCotizacionDolar(repo_cotizacion, repo_tipo),
    )

    ConsoleUI(servicios).run()


if __name__ == "__main__":
    main()
