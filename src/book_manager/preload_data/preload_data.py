"""Ejercicio 05: generación de los CSV de importación y carga inicial de datos.

Los archivos se escriben en book_manager/migrations/csv y luego se leen para
poblar el sistema a través de los servicios. Cada clase tiene al menos 10
registros. Los datos son de ejemplo (ISBN, editoriales y cotizaciones son
ilustrativos).
"""
import csv
import datetime
from pathlib import Path
from typing import Dict, List, Sequence

from book_manager.entities.entities import (
  CotizacionDolar, Editorial, Genero, Libro, Moneda, Precio, Stock, TipoCotizacion,
)
from book_manager.services.services import Servicios

CSV_DIR = Path(__file__).resolve().parent.parent / "migrations" / "csv"

# ------------------------------------------------------------------- datos
_GENEROS = ["Novela", "Ensayo", "Infantil", "Técnico", "Poesía",
            "Ciencia ficción", "Historia", "Biografía", "Policial", "Autoayuda"]

_EDITORIALES = [
  ("Sudamericana", "Argentina"), ("Planeta", "España"), ("Alfaguara", "España"),
  ("Anagrama", "España"), ("Tusquets", "España"), ("Siglo XXI", "Argentina"),
  ("O'Reilly Media", "Estados Unidos"), ("Fondo de Cultura Económica", "México"),
  ("Emecé", "Argentina"), ("Eudeba", "Argentina"),
]

_MONEDAS = [
  ("ARS", "Peso argentino", "$"), ("USD", "Dólar estadounidense", "US$"),
  ("EUR", "Euro", "€"), ("BRL", "Real brasileño", "R$"), ("GBP", "Libra esterlina", "£"),
  ("CLP", "Peso chileno", "CLP$"), ("UYU", "Peso uruguayo", "$U"),
  ("JPY", "Yen japonés", "¥"), ("CHF", "Franco suizo", "Fr."), ("MXN", "Peso mexicano", "MX$"),
]

_TIPOS = ["Oficial", "Blue", "MEP", "CCL", "Tarjeta",
          "Mayorista", "Solidario", "Cripto", "Ahorro", "Turista"]

# (isbn, título, autor, editorial_id, genero_id)
_LIBROS = [
  ("9789500000011", "Rayuela", "Julio Cortázar", 3, 1),
  ("9789500000028", "El Aleph", "Jorge Luis Borges", 9, 1),
  ("9789500000035", "Ficciones", "Jorge Luis Borges", 9, 1),
  ("9789500000042", "Sobre héroes y tumbas", "Ernesto Sabato", 1, 1),
  ("9781492056355", "Fluent Python", "Luciano Ramalho", 7, 4),
  ("9780132350884", "Clean Code", "Robert C. Martin", 7, 4),
  ("9789500000073", "Fundación", "Isaac Asimov", 2, 6),
  ("9789500000080", "Martín Fierro", "José Hernández", 10, 5),
  ("9789500000097", "Sapiens", "Yuval Noah Harari", 2, 7),
  ("9789500000103", "El Principito", "Antoine de Saint-Exupéry", 4, 3),
  ("9789500000110", "Estudio en escarlata", "Arthur Conan Doyle", 5, 9),
  ("9789500000127", "Las venas abiertas de América Latina", "Eduardo Galeano", 6, 2),
]

# (libro_id, moneda_id, valor): los libros técnicos importados van en USD
_PRECIOS = [
  (1, 1, "24500.00"), (2, 1, "18900.00"), (3, 1, "17500.00"), (4, 1, "21000.00"),
  (5, 2, "58.00"), (6, 2, "42.50"), (7, 1, "26800.00"), (8, 1, "12300.00"),
  (9, 1, "32000.00"), (10, 1, "9800.00"), (11, 1, "15400.00"), (12, 1, "19900.00"),
]

# (libro_id, cantidad)
_STOCK = [(1, 12), (2, 8), (3, 15), (4, 5), (5, 3), (6, 7),
          (7, 10), (8, 20), (9, 9), (10, 25), (11, 6), (12, 11)]

# (compra, venta) base por tipo; se generan 2 fechas por tipo (20 registros)
_COTIZ_BASE = [(1040, 1080), (1240, 1260), (1210, 1230), (1220, 1240), (1370, 1410),
               (1030, 1070), (1040, 1080), (1200, 1260), (1150, 1190), (1300, 1340)]
_FECHAS = ["2026-09-29", "2026-09-30"]


# ------------------------------------------------------------ generación CSV
def _escribir(directorio: Path, nombre: str, cabecera: Sequence[str], filas: List[Sequence]) -> None:
  with open(directorio / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cabecera)
    w.writerows(filas)


def generar_csvs(directorio: Path = CSV_DIR, sobrescribir: bool = False) -> None:
  """Escribe los CSV de importación. Si ya existen no los pisa (salvo sobrescribir=True)."""
  directorio.mkdir(parents=True, exist_ok=True)
  if not sobrescribir and (directorio / "libros.csv").exists():
    return
  _escribir(directorio, "generos", ["id", "nombre"], [(i, n) for i, n in enumerate(_GENEROS, 1)])
  _escribir(directorio, "editoriales", ["id", "nombre", "pais"],
            [(i, n, p) for i, (n, p) in enumerate(_EDITORIALES, 1)])
  _escribir(directorio, "monedas", ["id", "codigo", "nombre", "simbolo"],
            [(i, *m) for i, m in enumerate(_MONEDAS, 1)])
  _escribir(directorio, "tipos_cotizacion", ["id", "nombre"], [(i, n) for i, n in enumerate(_TIPOS, 1)])
  _escribir(directorio, "libros", ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"],
            [(i, *l) for i, l in enumerate(_LIBROS, 1)])
  _escribir(directorio, "precios", ["id", "libro_id", "moneda_id", "valor"],
            [(i, *p) for i, p in enumerate(_PRECIOS, 1)])
  _escribir(directorio, "stock", ["libro_id", "cantidad"], _STOCK)
  cotizaciones = []
  for tipo_id, (compra, venta) in enumerate(_COTIZ_BASE, 1):
    for n, fecha in enumerate(_FECHAS):
      cotizaciones.append((tipo_id, fecha, f"{compra + 5 * n:.2f}", f"{venta + 5 * n:.2f}"))
  _escribir(directorio, "cotizaciones", ["tipo_id", "fecha", "valor_compra", "valor_venta"], cotizaciones)


# ------------------------------------------------------------------- carga
def _leer(directorio: Path, nombre: str) -> List[Dict[str, str]]:
  with open(directorio / f"{nombre}.csv", newline="", encoding="utf-8") as f:
    return list(csv.DictReader(f))


def _obtener(servicio, id_: str, que: str):
  obj = servicio.obtener(int(id_))
  if obj is None:
    raise ValueError(f"CSV inconsistente: no existe {que} con id {id_}.")
  return obj


def cargar_datos(servicios: Servicios, directorio: Path = CSV_DIR) -> None:
  """Lee los CSV y crea las entidades usando los servicios (respeta el orden de dependencias)."""
  for f in _leer(directorio, "generos"):
    servicios.generos.crear(Genero(f["nombre"], id=int(f["id"])))
  for f in _leer(directorio, "editoriales"):
    servicios.editoriales.crear(Editorial(f["nombre"], f["pais"], id=int(f["id"])))
  for f in _leer(directorio, "monedas"):
    servicios.monedas.crear(Moneda(f["codigo"], f["nombre"], f["simbolo"], id=int(f["id"])))
  for f in _leer(directorio, "tipos_cotizacion"):
    servicios.tipos.crear(TipoCotizacion(f["nombre"], id=int(f["id"])))
  for f in _leer(directorio, "libros"):
    servicios.libros.crear(Libro(
      f["isbn"], f["titulo"], f["autor"],
      _obtener(servicios.editoriales, f["editorial_id"], "editorial"),
      _obtener(servicios.generos, f["genero_id"], "género"),
      id=int(f["id"])))
  for f in _leer(directorio, "precios"):
    servicios.precios.crear(Precio(
      _obtener(servicios.libros, f["libro_id"], "libro"),
      _obtener(servicios.monedas, f["moneda_id"], "moneda"),
      f["valor"], id=int(f["id"])))
  for f in _leer(directorio, "stock"):
    servicios.stock.crear(Stock(_obtener(servicios.libros, f["libro_id"], "libro"), int(f["cantidad"])))
  for f in _leer(directorio, "cotizaciones"):
    servicios.cotizaciones.crear(CotizacionDolar(
      _obtener(servicios.tipos, f["tipo_id"], "tipo de cotización"),
      datetime.date.fromisoformat(f["fecha"]),
      f["valor_compra"], f["valor_venta"]))


def precargar(servicios: Servicios, directorio: Path = CSV_DIR) -> None:
  """Genera los CSV (si hace falta) y carga los datos en el sistema."""
  generar_csvs(directorio)
  cargar_datos(servicios, directorio)


if __name__ == "__main__":
  generar_csvs(sobrescribir=True)
  print(f"CSV generados en {CSV_DIR}")
