"""Ejercicio 05: generación de los CSV de importación.

Los archivos se escriben en book_manager/migrations/csv y son los mismos que
leen y guardan los repositorios. Cada clase tiene al menos 10 registros. Los
datos son de ejemplo (los ISBN son ilustrativos).
"""
import csv
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

CSV_DIR = Path(__file__).resolve().parent.parent / "migrations" / "csv"

_GENEROS = [
    "Novela", "Ensayo", "Infantil", "Técnico", "Poesía",
    "Ciencia ficción", "Historia", "Biografía", "Policial", "Autoayuda",
]

_EDITORIALES = [
    "Sudamericana", "Planeta", "Alfaguara", "Anagrama", "Tusquets",
    "Siglo XXI", "O'Reilly Media", "Fondo de Cultura Económica", "Emecé",
    "Eudeba",
]

_MONEDAS = [
    ("ARS", "Peso argentino"), ("USD", "Dólar estadounidense"),
    ("EUR", "Euro"), ("BRL", "Real brasileño"), ("GBP", "Libra esterlina"),
    ("CLP", "Peso chileno"), ("UYU", "Peso uruguayo"), ("JPY", "Yen japonés"),
    ("CHF", "Franco suizo"), ("MXN", "Peso mexicano"),
]

_TIPOS = [
    "Oficial", "Blue", "MEP", "CCL", "Tarjeta",
    "Mayorista", "Solidario", "Cripto", "Ahorro", "Turista",
]

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
    ("9789500000127", "Las venas abiertas de América Latina",
     "Eduardo Galeano", 6, 2),
]

# (libro_id, moneda_id, valor): los libros técnicos importados van en USD
_PRECIOS = [
    (1, 1, 24500.0), (2, 1, 18900.0), (3, 1, 17500.0), (4, 1, 21000.0),
    (5, 2, 58.0), (6, 2, 42.5), (7, 1, 26800.0), (8, 1, 12300.0),
    (9, 1, 32000.0), (10, 1, 9800.0), (11, 1, 15400.0), (12, 1, 19900.0),
]

# (libro_id, cantidad)
_STOCK = [
    (1, 12), (2, 8), (3, 15), (4, 5), (5, 3), (6, 7),
    (7, 10), (8, 20), (9, 9), (10, 25), (11, 6), (12, 11),
]

# Valor de venta por tipo de cotización (en orden de id); 2 fechas por tipo
_VALORES_VENTA = [1080, 1260, 1230, 1240, 1410, 1070, 1080, 1260, 1190, 1340]
_FECHAS = ["2026-09-29", "2026-09-30"]


def _con_id(filas: Sequence[Tuple]) -> List[Tuple]:
    """Antepone un id correlativo (desde 1) a cada fila."""
    return [(i, *fila) for i, fila in enumerate(filas, 1)]


_TABLAS: Dict[str, Tuple[List[str], List[Tuple]]] = {
    "generos": (["id", "nombre"], _con_id([(n,) for n in _GENEROS])),
    "editoriales": (["id", "nombre"], _con_id([(n,) for n in _EDITORIALES])),
    "monedas": (["id", "codigo", "nombre"], _con_id(_MONEDAS)),
    "tipos_cotizacion": (["id", "nombre"], _con_id([(n,) for n in _TIPOS])),
    "libros": (
        ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"],
        _con_id(_LIBROS),
    ),
    "precios": (["id", "libro_id", "moneda_id", "valor"], _con_id(_PRECIOS)),
    "stock": (["libro_id", "cantidad"], _STOCK),
    "cotizaciones": (
        ["tipo_id", "fecha", "valor"],
        [
            (tipo_id, fecha, float(venta + 5 * n))
            for tipo_id, venta in enumerate(_VALORES_VENTA, 1)
            for n, fecha in enumerate(_FECHAS)
        ],
    ),
}


def generar_csvs(
    directorio: Path = CSV_DIR, sobrescribir: bool = False
) -> None:
    """Escribe los CSV de importación en el directorio indicado.

    Args:
        directorio (Path): Carpeta donde se escriben los archivos.
        sobrescribir (bool): Si es False, no pisa los archivos que ya existen.
    """
    directorio.mkdir(parents=True, exist_ok=True)
    for nombre, (cabecera, filas) in _TABLAS.items():
        ruta = directorio / f"{nombre}.csv"
        if ruta.exists() and not sobrescribir:
            continue
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(cabecera)
            escritor.writerows(filas)


if __name__ == "__main__":
    generar_csvs(sobrescribir=True)
    print(f"CSV generados en {CSV_DIR}")
