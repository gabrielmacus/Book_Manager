"""Migración de los datos de los CSV a la base de datos y generación de SQL."""
from pathlib import Path

from sqlalchemy import Insert, delete, insert
from sqlalchemy.dialects import postgresql

from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    CotizacionDolarModel,
    EditorialModel,
    GeneroModel,
    LibroModel,
    MonedaModel,
    PrecioModel,
    StockModel,
    TipoCotizacionModel,
    crear_tablas,
)
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolarCsv,
    RepositorioEditorialCsv,
    RepositorioGeneroCsv,
    RepositorioLibroCsv,
    RepositorioMonedaCsv,
    RepositorioPrecioCsv,
    RepositorioStockCsv,
    RepositorioTipoCotizacionCsv,
)


def _a_texto_sql(sentencia: Insert) -> str:
    """Convierte una sentencia INSERT en texto SQL con los valores incluidos.

    Args:
        sentencia: Sentencia de inserción de SQLAlchemy.

    Returns:
        La sentencia como texto SQL de PostgreSQL, terminada en punto y coma.
    """
    texto = sentencia.compile(
        dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
    )
    return f"{texto};"


def migrar_datos(carpeta_csvs: str, carpeta_sqls: str) -> None:
  """ Función encargada de la migración de datos de csv a sql.
  Se encarga de leer los archivos csv y crear los archivos sql
  para la inserción en la base de datos.

  Args:
      carpeta_csvs (str): Carpeta donde se encuentran los archivos csv de origen.
      carpeta_sqls (str): Carpeta donde se deben guardar los archivos sql generados.
  """
  origen = Path(carpeta_csvs)
  destino = Path(carpeta_sqls)
  destino.mkdir(parents=True, exist_ok=True)

  # Tablas en orden de dependencias: (archivo sql, modelo, filas a insertar).
  tablas = [
      ("01_generos.sql", GeneroModel, [
          {"id": g.id, "nombre": g.nombre}
          for g in RepositorioGeneroCsv(origen / "generos.csv").leer_todos()]),
      ("02_editoriales.sql", EditorialModel, [
          {"id": e.id, "nombre": e.nombre}
          for e in RepositorioEditorialCsv(origen / "editoriales.csv").leer_todos()]),
      ("03_monedas.sql", MonedaModel, [
          {"id": m.id, "codigo": m.codigo, "nombre": m.nombre}
          for m in RepositorioMonedaCsv(origen / "monedas.csv").leer_todos()]),
      ("04_tipos_cotizacion.sql", TipoCotizacionModel, [
          {"id": t.id, "nombre": t.nombre}
          for t in RepositorioTipoCotizacionCsv(
              origen / "tipos_cotizacion.csv").leer_todos()]),
      ("05_libros.sql", LibroModel, [
          {"id": l.id, "isbn": l.isbn, "titulo": l.titulo, "autor": l.autor,
           "editorial_id": l.editorial_id, "genero_id": l.genero_id}
          for l in RepositorioLibroCsv(origen / "libros.csv").leer_todos()]),
      ("06_precios.sql", PrecioModel, [
          {"id": p.id, "libro_id": p.libro_id, "moneda_id": p.moneda_id,
           "valor": p.valor}
          for p in RepositorioPrecioCsv(origen / "precios.csv").leer_todos()]),
      ("07_stock.sql", StockModel, [
          {"libro_id": s.libro_id, "cantidad": s.cantidad}
          for s in RepositorioStockCsv(origen / "stock.csv").leer_todos()]),
      ("08_cotizaciones.sql", CotizacionDolarModel, [
          {"tipo_id": c.tipo_id, "fecha": c.fecha, "valor": c.valor}
          for c in RepositorioCotizacionDolarCsv(
              origen / "cotizaciones.csv").leer_todos()]),
  ]

  conexion = ConexionDB()
  try:
    crear_tablas(conexion)
    with conexion.transaccion() as sesion:
      # Se borra en orden inverso para poder volver a migrar sin duplicar.
      for _, modelo, _ in reversed(tablas):
        sesion.execute(delete(modelo))

      for archivo, modelo, filas in tablas:
        sentencias = [insert(modelo).values(**fila) for fila in filas]
        for sentencia in sentencias:
          sesion.execute(sentencia)
        lineas = [_a_texto_sql(sentencia) for sentencia in sentencias]
        (destino / archivo).write_text("\n".join(lineas) + "\n", encoding="utf-8")
  finally:
    conexion.cerrar()
