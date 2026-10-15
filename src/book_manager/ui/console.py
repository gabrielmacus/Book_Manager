"""Interfaz de consola de Book Manager."""
import csv
import datetime
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from requests import RequestException

from book_manager.services.services import Servicios

EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"


class ConsoleUI:
    """Interfaz de usuario por consola."""

    def __init__(self, servicios: Servicios) -> None:
        """Inicializa la interfaz con el contenedor de servicios.

        Args:
            servicios (Servicios): Contenedor con los servicios de la
                aplicación.
        """
        self.servicios = servicios

    def _clear_screen(self) -> None:
        """Limpia la terminal; en notebooks solo imprime un separador.

        En Colab no se borra la salida para que quede registro de todas las
        operaciones realizadas y el cuadro de input se muestre siempre.
        """
        try:
            from IPython import get_ipython

            en_notebook = hasattr(get_ipython(), "kernel")
        except ImportError:
            en_notebook = False
        if en_notebook:
            print("\n" + "=" * 60)
        else:
            os.system("cls" if os.name == "nt" else "clear")

    def _get_input(self, prompt: str, tipo: type = str) -> Any:
        while True:
            try:
                valor = input(prompt).strip()
                if tipo == int:
                    return int(valor)
                elif tipo == float:
                    return float(valor)
                return valor
            except ValueError:
                print("Entrada inválida. Intente de nuevo.")

    def _pause(self) -> None:
        input("\nPresione Enter para continuar...")

    def _referencia(
        self, servicio: Any, id: int, atributo: str = "nombre"
    ) -> str:
        """Retorna 'valor (id)' del registro relacionado, o solo el id."""
        registro = servicio.obtener_por_id(id)
        if registro is None:
            return str(id)
        return f"{getattr(registro, atributo)} ({id})"

    def _editorial(self, id: int) -> str:
        return self._referencia(self.servicios.editoriales, id)

    def _genero(self, id: int) -> str:
        return self._referencia(self.servicios.generos, id)

    def _libro(self, id: int) -> str:
        return self._referencia(self.servicios.libros, id, "titulo")

    def _moneda(self, id: int) -> str:
        return self._referencia(self.servicios.monedas, id, "codigo")

    def _tipo(self, id: int) -> str:
        return self._referencia(self.servicios.tipos, id)

    def _display_list(
        self,
        titulo: str,
        items: List[Any],
        formateador: Callable[[Any], str],
    ) -> None:
        self._clear_screen()
        print(f"--- {titulo} ---")
        if not items:
            print("No hay registros.")
        else:
            for item in items:
                print(formateador(item))
        self._pause()

    def _crear_genero(self) -> None:
        self._clear_screen()
        print("--- Crear Género ---")
        id = self.servicios.generos.siguiente_id()
        nombre = self._get_input("Nombre del género: ")
        try:
            genero = self.servicios.generos.crear(id, nombre)
            print(f"Género creado: ID {genero.id} - {genero.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_generos(self) -> None:
        self._display_list(
            "Listado de Géneros",
            self.servicios.generos.obtener_todos(),
            lambda g: f"ID: {g.id} | Nombre: {g.nombre}",
        )

    def _buscar_genero(self) -> None:
        self._clear_screen()
        print("--- Buscar Género por ID ---")
        id = self._get_input("ID a buscar: ", int)
        genero = self.servicios.generos.obtener_por_id(id)
        if genero:
            print(f"ID: {genero.id} | Nombre: {genero.nombre}")
        else:
            print(f"No se encontró un género con ID {id}.")
        self._pause()

    def _actualizar_genero(self) -> None:
        self._clear_screen()
        print("--- Actualizar Género ---")
        id = self._get_input("ID del género a actualizar: ", int)
        nuevo_nombre = self._get_input("Nuevo nombre: ")
        try:
            genero = self.servicios.generos.actualizar(id, nuevo_nombre)
            print(f"Género actualizado: ID {genero.id} - {genero.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_genero(self) -> None:
        self._clear_screen()
        print("--- Eliminar Género ---")
        id = self._get_input("ID del género a eliminar: ", int)
        try:
            if self.servicios.generos.eliminar(id):
                print(f"Género {id} eliminado exitosamente.")
            else:
                print(f"No se encontró un género con ID {id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_generos(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Géneros ---")
            print("1. Crear Género")
            print("2. Listar Géneros")
            print("3. Buscar Género por ID")
            print("4. Actualizar Género")
            print("5. Eliminar Género")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_genero()
            elif opcion == 2:
                self._listar_generos()
            elif opcion == 3:
                self._buscar_genero()
            elif opcion == 4:
                self._actualizar_genero()
            elif opcion == 5:
                self._eliminar_genero()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_editorial(self) -> None:
        self._clear_screen()
        print("--- Crear Editorial ---")
        id = self.servicios.editoriales.siguiente_id()
        nombre = self._get_input("Nombre de la editorial: ")
        try:
            editorial = self.servicios.editoriales.crear(id, nombre)
            print(f"Editorial creada: ID {editorial.id} - {editorial.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_editoriales(self) -> None:
        self._display_list(
            "Listado de Editoriales",
            self.servicios.editoriales.obtener_todos(),
            lambda e: f"ID: {e.id} | Nombre: {e.nombre}",
        )

    def _buscar_editorial(self) -> None:
        self._clear_screen()
        print("--- Buscar Editorial por ID ---")
        id = self._get_input("ID a buscar: ", int)
        editorial = self.servicios.editoriales.obtener_por_id(id)
        if editorial:
            print(f"ID: {editorial.id} | Nombre: {editorial.nombre}")
        else:
            print(f"No se encontró una editorial con ID {id}.")
        self._pause()

    def _actualizar_editorial(self) -> None:
        self._clear_screen()
        print("--- Actualizar Editorial ---")
        id = self._get_input("ID de la editorial a actualizar: ", int)
        nuevo_nombre = self._get_input("Nuevo nombre: ")
        try:
            editorial = self.servicios.editoriales.actualizar(id, nuevo_nombre)
            print(
                f"Editorial actualizada: ID {editorial.id} - "
                f"{editorial.nombre}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_editorial(self) -> None:
        self._clear_screen()
        print("--- Eliminar Editorial ---")
        id = self._get_input("ID de la editorial a eliminar: ", int)
        try:
            if self.servicios.editoriales.eliminar(id):
                print(f"Editorial {id} eliminada exitosamente.")
            else:
                print(f"No se encontró una editorial con ID {id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_editoriales(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Editoriales ---")
            print("1. Crear Editorial")
            print("2. Listar Editoriales")
            print("3. Buscar Editorial por ID")
            print("4. Actualizar Editorial")
            print("5. Eliminar Editorial")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_editorial()
            elif opcion == 2:
                self._listar_editoriales()
            elif opcion == 3:
                self._buscar_editorial()
            elif opcion == 4:
                self._actualizar_editorial()
            elif opcion == 5:
                self._eliminar_editorial()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_libro(self) -> None:
        self._clear_screen()
        print("--- Crear Libro ---")
        id = self.servicios.libros.siguiente_id()
        isbn = self._get_input("ISBN: ")
        titulo = self._get_input("Título: ")
        autor = self._get_input("Autor: ")
        editorial_id = self._get_input("ID Editorial: ", int)
        genero_id = self._get_input("ID Género: ", int)
        try:
            libro = self.servicios.libros.crear(
                id, isbn, titulo, autor, editorial_id, genero_id
            )
            print(
                f"Libro creado: ID {libro.id} - '{libro.titulo}' "
                f"de {libro.autor}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_libros(self) -> None:
        self._display_list(
            "Listado de Libros",
            self.servicios.libros.obtener_todos(),
            lambda libro: (
                f"ID: {libro.id} | ISBN: {libro.isbn} | "
                f"Título: {libro.titulo} | Autor: {libro.autor} | "
                f"Editorial: {self._editorial(libro.editorial_id)} | "
                f"Género: {self._genero(libro.genero_id)}"
            ),
        )

    def _buscar_libro(self) -> None:
        self._clear_screen()
        print("--- Buscar Libro por ID ---")
        id = self._get_input("ID a buscar: ", int)
        libro = self.servicios.libros.obtener_por_id(id)
        if libro:
            print(
                f"ID: {libro.id} | ISBN: {libro.isbn} | "
                f"Título: {libro.titulo} | Autor: {libro.autor} | "
                f"Editorial: {self._editorial(libro.editorial_id)} | "
                f"Género: {self._genero(libro.genero_id)}"
            )
        else:
            print(f"No se encontró un libro con ID {id}.")
        self._pause()

    def _actualizar_libro(self) -> None:
        self._clear_screen()
        print("--- Actualizar Libro ---")
        id = self._get_input("ID a actualizar: ", int)
        isbn = self._get_input("Nuevo ISBN: ")
        titulo = self._get_input("Nuevo título: ")
        autor = self._get_input("Nuevo autor: ")
        editorial_id = self._get_input("Nuevo ID Editorial: ", int)
        genero_id = self._get_input("Nuevo ID Género: ", int)
        try:
            libro = self.servicios.libros.actualizar(
                id, isbn, titulo, autor, editorial_id, genero_id
            )
            print(f"Libro actualizado: ID {libro.id} - '{libro.titulo}'")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_libro(self) -> None:
        self._clear_screen()
        print("--- Eliminar Libro ---")
        id = self._get_input("ID a eliminar: ", int)
        try:
            if self.servicios.libros.eliminar(id):
                print(f"Libro {id} eliminado exitosamente.")
            else:
                print(f"No se encontró un libro con ID {id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_libros(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Libros ---")
            print("1. Crear Libro")
            print("2. Listar Libros")
            print("3. Buscar Libro por ID")
            print("4. Actualizar Libro")
            print("5. Eliminar Libro")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_libro()
            elif opcion == 2:
                self._listar_libros()
            elif opcion == 3:
                self._buscar_libro()
            elif opcion == 4:
                self._actualizar_libro()
            elif opcion == 5:
                self._eliminar_libro()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_moneda(self) -> None:
        self._clear_screen()
        print("--- Crear Moneda ---")
        id = self.servicios.monedas.siguiente_id()
        codigo = self._get_input("Código (ej: ARS, USD): ")
        nombre = self._get_input("Nombre: ")
        try:
            moneda = self.servicios.monedas.crear(id, codigo, nombre)
            print(
                f"Moneda creada: ID {moneda.id} - {moneda.codigo} "
                f"({moneda.nombre})"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_monedas(self) -> None:
        self._display_list(
            "Listado de Monedas",
            self.servicios.monedas.obtener_todos(),
            lambda m: f"ID: {m.id} | Código: {m.codigo} | Nombre: {m.nombre}",
        )

    def _buscar_moneda(self) -> None:
        self._clear_screen()
        print("--- Buscar Moneda por ID ---")
        id = self._get_input("ID a buscar: ", int)
        moneda = self.servicios.monedas.obtener_por_id(id)
        if moneda:
            print(
                f"ID: {moneda.id} | Código: {moneda.codigo} | "
                f"Nombre: {moneda.nombre}"
            )
        else:
            print(f"No se encontró una moneda con ID {id}.")
        self._pause()

    def _actualizar_moneda(self) -> None:
        self._clear_screen()
        print("--- Actualizar Moneda ---")
        id = self._get_input("ID a actualizar: ", int)
        codigo = self._get_input("Nuevo código: ")
        nombre = self._get_input("Nuevo nombre: ")
        try:
            moneda = self.servicios.monedas.actualizar(id, codigo, nombre)
            print(
                f"Moneda actualizada: ID {moneda.id} - {moneda.codigo} "
                f"({moneda.nombre})"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_moneda(self) -> None:
        self._clear_screen()
        print("--- Eliminar Moneda ---")
        id = self._get_input("ID a eliminar: ", int)
        try:
            if self.servicios.monedas.eliminar(id):
                print(f"Moneda {id} eliminada exitosamente.")
            else:
                print(f"No se encontró una moneda con ID {id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_monedas(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Monedas ---")
            print("1. Crear Moneda")
            print("2. Listar Monedas")
            print("3. Buscar Moneda por ID")
            print("4. Actualizar Moneda")
            print("5. Eliminar Moneda")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_moneda()
            elif opcion == 2:
                self._listar_monedas()
            elif opcion == 3:
                self._buscar_moneda()
            elif opcion == 4:
                self._actualizar_moneda()
            elif opcion == 5:
                self._eliminar_moneda()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_tipo_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Crear Tipo de Cotización ---")
        id = self.servicios.tipos.siguiente_id()
        nombre = self._get_input("Nombre (ej: Oficial, Blue): ")
        try:
            tipo = self.servicios.tipos.crear(id, nombre)
            print(f"Tipo creado: ID {tipo.id} - {tipo.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_tipos_cotizacion(self) -> None:
        self._display_list(
            "Listado de Tipos de Cotización",
            self.servicios.tipos.obtener_todos(),
            lambda t: f"ID: {t.id} | Nombre: {t.nombre}",
        )

    def _buscar_tipo_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Buscar Tipo de Cotización por ID ---")
        id = self._get_input("ID a buscar: ", int)
        tipo = self.servicios.tipos.obtener_por_id(id)
        if tipo:
            print(f"ID: {tipo.id} | Nombre: {tipo.nombre}")
        else:
            print(f"No se encontró un tipo de cotización con ID {id}.")
        self._pause()

    def _actualizar_tipo_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Actualizar Tipo de Cotización ---")
        id = self._get_input("ID a actualizar: ", int)
        nombre = self._get_input("Nuevo nombre: ")
        try:
            tipo = self.servicios.tipos.actualizar(id, nombre)
            print(f"Tipo actualizado: ID {tipo.id} - {tipo.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_tipo_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Eliminar Tipo de Cotización ---")
        id = self._get_input("ID a eliminar: ", int)
        try:
            if self.servicios.tipos.eliminar(id):
                print(f"Tipo de cotización {id} eliminado exitosamente.")
            else:
                print(f"No se encontró un tipo de cotización con ID {id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_tipos_cotizacion(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Tipos de Cotización ---")
            print("1. Crear Tipo de Cotización")
            print("2. Listar Tipos de Cotización")
            print("3. Buscar Tipo de Cotización por ID")
            print("4. Actualizar Tipo de Cotización")
            print("5. Eliminar Tipo de Cotización")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_tipo_cotizacion()
            elif opcion == 2:
                self._listar_tipos_cotizacion()
            elif opcion == 3:
                self._buscar_tipo_cotizacion()
            elif opcion == 4:
                self._actualizar_tipo_cotizacion()
            elif opcion == 5:
                self._eliminar_tipo_cotizacion()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_precio(self) -> None:
        self._clear_screen()
        print("--- Crear Precio ---")
        id = self.servicios.precios.siguiente_id()
        libro_id = self._get_input("ID Libro: ", int)
        moneda_id = self._get_input("ID Moneda: ", int)
        valor = self._get_input("Valor: ", float)
        try:
            precio = self.servicios.precios.crear(
                id, libro_id, moneda_id, valor
            )
            print(
                f"Precio creado: ID {precio.id} | "
                f"Libro {self._libro(precio.libro_id)} | "
                f"Moneda {self._moneda(precio.moneda_id)} | "
                f"Valor: {precio.valor}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_precios(self) -> None:
        self._display_list(
            "Listado de Precios",
            self.servicios.precios.obtener_todos(),
            lambda p: (
                f"ID: {p.id} | Libro: {self._libro(p.libro_id)} | "
                f"Moneda: {self._moneda(p.moneda_id)} | Valor: {p.valor}"
            ),
        )

    def _buscar_precio(self) -> None:
        self._clear_screen()
        print("--- Buscar Precio por ID ---")
        id = self._get_input("ID a buscar: ", int)
        precio = self.servicios.precios.obtener_por_id(id)
        if precio:
            print(
                f"ID: {precio.id} | Libro: {self._libro(precio.libro_id)} | "
                f"Moneda: {self._moneda(precio.moneda_id)} | "
                f"Valor: {precio.valor}"
            )
        else:
            print(f"No se encontró un precio con ID {id}.")
        self._pause()

    def _listar_precios_por_libro(self) -> None:
        self._clear_screen()
        print("--- Listar Precios por Libro ---")
        libro_id = self._get_input("ID Libro: ", int)
        precios = self.servicios.precios.obtener_por_libro(libro_id)
        self._display_list(
            f"Precios del Libro {self._libro(libro_id)}",
            precios,
            lambda p: (
                f"ID: {p.id} | Moneda: {self._moneda(p.moneda_id)} | "
                f"Valor: {p.valor}"
            ),
        )

    def _actualizar_precio(self) -> None:
        self._clear_screen()
        print("--- Actualizar Precio ---")
        id = self._get_input("ID a actualizar: ", int)
        libro_id = self._get_input("Nuevo ID Libro: ", int)
        moneda_id = self._get_input("Nuevo ID Moneda: ", int)
        valor = self._get_input("Nuevo valor: ", float)
        try:
            precio = self.servicios.precios.actualizar(
                id, libro_id, moneda_id, valor
            )
            print(
                f"Precio actualizado: ID {precio.id} | Valor: {precio.valor}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_precio(self) -> None:
        self._clear_screen()
        print("--- Eliminar Precio ---")
        id = self._get_input("ID a eliminar: ", int)
        try:
            if self.servicios.precios.eliminar(id):
                print(f"Precio {id} eliminado exitosamente.")
            else:
                print(f"No se encontró un precio con ID {id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_precios(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Precios ---")
            print("1. Crear Precio")
            print("2. Listar Precios")
            print("3. Buscar Precio por ID")
            print("4. Listar Precios por Libro")
            print("5. Actualizar Precio")
            print("6. Eliminar Precio")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_precio()
            elif opcion == 2:
                self._listar_precios()
            elif opcion == 3:
                self._buscar_precio()
            elif opcion == 4:
                self._listar_precios_por_libro()
            elif opcion == 5:
                self._actualizar_precio()
            elif opcion == 6:
                self._eliminar_precio()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_stock(self) -> None:
        self._clear_screen()
        print("--- Registrar Stock ---")
        libro_id = self._get_input("ID Libro: ", int)
        cantidad = self._get_input("Cantidad: ", int)
        try:
            stock = self.servicios.stock.crear(libro_id, cantidad)
            print(
                f"Stock registrado: Libro {self._libro(stock.libro_id)} | "
                f"Cantidad: {stock.cantidad}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_stock(self) -> None:
        self._display_list(
            "Listado de Stock",
            self.servicios.stock.obtener_todos(),
            lambda s: (
                f"Libro: {self._libro(s.libro_id)} | Cantidad: {s.cantidad}"
            ),
        )

    def _buscar_stock(self) -> None:
        self._clear_screen()
        print("--- Buscar Stock por ID de Libro ---")
        libro_id = self._get_input("ID Libro a consultar: ", int)
        stock = self.servicios.stock.obtener_por_libro(libro_id)
        if stock:
            print(
                f"Libro: {self._libro(stock.libro_id)} | "
                f"Cantidad: {stock.cantidad}"
            )
        else:
            print(
                "No se encontró stock registrado para el libro "
                f"{libro_id}."
            )
        self._pause()

    def _actualizar_stock(self) -> None:
        self._clear_screen()
        print("--- Actualizar Stock ---")
        libro_id = self._get_input("ID Libro a actualizar: ", int)
        cantidad = self._get_input("Nueva cantidad: ", int)
        try:
            stock = self.servicios.stock.actualizar(libro_id, cantidad)
            print(
                f"Stock actualizado: Libro {self._libro(stock.libro_id)} | "
                f"Cantidad: {stock.cantidad}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_stock(self) -> None:
        self._clear_screen()
        print("--- Eliminar Stock ---")
        libro_id = self._get_input("ID Libro a eliminar stock: ", int)
        try:
            if self.servicios.stock.eliminar(libro_id):
                print(f"Stock del libro {libro_id} eliminado exitosamente.")
            else:
                print(
                    "No se encontró stock registrado para el libro "
                    f"{libro_id}."
                )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_stock(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Stock ---")
            print("1. Registrar Stock")
            print("2. Listar Stock")
            print("3. Buscar Stock por ID de Libro")
            print("4. Actualizar Stock")
            print("5. Eliminar Stock")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_stock()
            elif opcion == 2:
                self._listar_stock()
            elif opcion == 3:
                self._buscar_stock()
            elif opcion == 4:
                self._actualizar_stock()
            elif opcion == 5:
                self._eliminar_stock()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _crear_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Registrar Cotización de Dólar ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        valor = self._get_input("Valor: ", float)
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            cotiz = self.servicios.cotizaciones.crear(tipo_id, fecha, valor)
            print(
                f"Cotización registrada: Tipo {self._tipo(cotiz.tipo_id)} | "
                f"Fecha {cotiz.fecha} | Valor: {cotiz.valor}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _consultar_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Consultar Cotización por Tipo y Fecha ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            cotiz = self.servicios.cotizaciones.obtener_por_tipo_y_fecha(
                tipo_id, fecha
            )
            if cotiz:
                print(
                    f"Tipo: {self._tipo(cotiz.tipo_id)} | "
                    f"Fecha: {cotiz.fecha} | "
                    f"Valor: {cotiz.valor}"
                )
            else:
                print("No se encontró cotización para ese tipo y fecha.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _historico_cotizaciones(self) -> None:
        self._clear_screen()
        print("--- Histórico de Cotizaciones por Tipo ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        historico = self.servicios.cotizaciones.obtener_historico_por_tipo(
            tipo_id
        )
        self._display_list(
            f"Histórico de Cotizaciones - Tipo {self._tipo(tipo_id)}",
            historico,
            lambda c: f"Fecha: {c.fecha} | Valor: {c.valor}",
        )

    def _ultima_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Última Cotización de un Tipo ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        cotiz = self.servicios.cotizaciones.obtener_ultima_cotizacion(tipo_id)
        if cotiz:
            print(
                f"Última cotización -> Fecha: {cotiz.fecha} | "
                f"Valor: {cotiz.valor}"
            )
        else:
            print("No hay cotizaciones registradas para ese tipo.")
        self._pause()

    def _actualizar_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Actualizar Cotización ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        valor = self._get_input("Nuevo valor: ", float)
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            cotiz = self.servicios.cotizaciones.actualizar(
                tipo_id, fecha, valor
            )
            print(
                f"Cotización actualizada: Tipo {self._tipo(cotiz.tipo_id)} | "
                f"Fecha {cotiz.fecha} | Valor: {cotiz.valor}"
            )
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_cotizacion(self) -> None:
        self._clear_screen()
        print("--- Eliminar Cotización ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            if self.servicios.cotizaciones.eliminar(tipo_id, fecha):
                print("Cotización eliminada exitosamente.")
            else:
                print("No se encontró la cotización especificada.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_cotizaciones_dolar(self) -> None:
        while True:
            self._clear_screen()
            print("\n--- Gestión de Cotizaciones de Dólar ---")
            print("1. Registrar Cotización")
            print("2. Consultar Cotización por Tipo y Fecha")
            print("3. Ver Histórico por Tipo")
            print("4. Ver Última Cotización de un Tipo")
            print("5. Actualizar Cotización")
            print("6. Eliminar Cotización")
            print("0. Volver al Menú Principal")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self._crear_cotizacion()
            elif opcion == 2:
                self._consultar_cotizacion()
            elif opcion == 3:
                self._historico_cotizaciones()
            elif opcion == 4:
                self._ultima_cotizacion()
            elif opcion == 5:
                self._actualizar_cotizacion()
            elif opcion == 6:
                self._eliminar_cotizacion()
            elif opcion == 0:
                break
            else:
                print("Opción inválida.")
                self._pause()

    def _obtener_cotizaciones_api(self) -> None:
        self._clear_screen()
        print("--- Obtener Cotizaciones por API ---")
        try:
            cotizaciones = self.servicios.cotizaciones.obtener_cotizaciones()
        except (RequestException, ValueError) as e:
            print(f"Error: {e}")
            self._pause()
            return
        self._display_list(
            "Cotizaciones registradas desde la API",
            cotizaciones,
            lambda c: (
                f"Tipo: {self._tipo(c.tipo_id)} | Fecha: {c.fecha} | "
                f"Valor: {c.valor}"
            ),
        )

    def _precios_por_libro(self) -> Dict[int, Dict[str, float]]:
        """Retorna {libro_id: {código de moneda: valor}} de los precios."""
        codigos = {
            m.id: m.codigo for m in self.servicios.monedas.obtener_todos()
        }
        precios: Dict[int, Dict[str, float]] = {}
        for p in self.servicios.precios.obtener_todos():
            precios.setdefault(p.libro_id, {})[codigos[p.moneda_id]] = p.valor
        return precios

    def _precio_en(
        self, valores: Dict[str, float], codigo: str, dolar: Optional[float]
    ) -> str:
        """Retorna el precio en la moneda pedida, convirtiendo ARS/USD.

        Args:
            valores (Dict[str, float]): Precios del libro por código.
            codigo (str): Código de la moneda a mostrar.
            dolar (Optional[float]): Cotización para convertir, o None.

        Returns:
            str: El precio con dos decimales, o '-' si no se puede obtener.
        """
        if codigo in valores:
            return f"{valores[codigo]:.2f}"
        if dolar and codigo == "ARS" and "USD" in valores:
            return f"{valores['USD'] * dolar:.2f}"
        if dolar and codigo == "USD" and "ARS" in valores:
            return f"{valores['ARS'] / dolar:.2f}"
        return "-"

    def _lista_bimonetaria(self) -> None:
        self._clear_screen()
        print("--- Lista de Precios Bimonetaria ---")
        for m in self.servicios.monedas.obtener_todos():
            print(f"{m.id}. {m.codigo} - {m.nombre}")
        moneda_id = self._get_input("ID de la moneda: ", int)
        moneda = self.servicios.monedas.obtener_por_id(moneda_id)
        if moneda is None:
            print(f"No se encontró una moneda con ID {moneda_id}.")
            self._pause()
            return
        for t in self.servicios.tipos.obtener_todos():
            print(f"{t.id}. {t.nombre}")
        tipo_id = self._get_input("ID del tipo de cotización: ", int)
        ultima = self.servicios.cotizaciones.obtener_ultima_cotizacion(
            tipo_id
        )
        dolar = ultima.valor if ultima else None
        precios = self._precios_por_libro()

        def fila(libro: Any) -> str:
            valores = precios.get(libro.id, {})
            ars = self._precio_en(valores, "ARS", dolar)
            otra = self._precio_en(valores, moneda.codigo, dolar)
            return f"{libro.titulo} | ARS: {ars} | {moneda.codigo}: {otra}"

        self._display_list(
            f"Precios en ARS y {moneda.codigo} (dólar {self._tipo(tipo_id)}: "
            f"{dolar if dolar else 'sin cotización'})",
            self.servicios.libros.obtener_todos(),
            fila,
        )

    def _exportar_precios_csv(self) -> None:
        self._clear_screen()
        print("--- Exportar Precios a CSV ---")
        codigos = [m.codigo for m in self.servicios.monedas.obtener_todos()]
        precios = self._precios_por_libro()
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ruta = EXPORTS_DIR / "precios.csv"
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["isbn", "titulo", *codigos])
            for libro in self.servicios.libros.obtener_todos():
                valores = precios.get(libro.id, {})
                escritor.writerow(
                    [libro.isbn, libro.titulo,
                     *(valores.get(c, "") for c in codigos)]
                )
        print(f"Precios exportados en {ruta}")
        self._pause()

    def run(self) -> None:
        while True:
            self._clear_screen()
            print("\n===== MENÚ PRINCIPAL BOOK MANAGER =====")
            print("1. Gestión de Géneros")
            print("2. Gestión de Editoriales")
            print("3. Gestión de Libros")
            print("4. Gestión de Monedas")
            print("5. Gestión de Tipos de Cotización")
            print("6. Gestión de Precios")
            print("7. Gestión de Stock")
            print("8. Gestión de Cotizaciones Dólar")
            print("9. Obtener Cotizaciones por API")
            print("10. Lista de Precios Bimonetaria")
            print("11. Exportar Precios a CSV")
            print("0. Salir")
            opcion = self._get_input("Seleccione una opción: ", int)

            if opcion == 1:
                self.manage_generos()
            elif opcion == 2:
                self.manage_editoriales()
            elif opcion == 3:
                self.manage_libros()
            elif opcion == 4:
                self.manage_monedas()
            elif opcion == 5:
                self.manage_tipos_cotizacion()
            elif opcion == 6:
                self.manage_precios()
            elif opcion == 7:
                self.manage_stock()
            elif opcion == 8:
                self.manage_cotizaciones_dolar()
            elif opcion == 9:
                self._obtener_cotizaciones_api()
            elif opcion == 10:
                self._lista_bimonetaria()
            elif opcion == 11:
                self._exportar_precios_csv()
            elif opcion == 0:
                print("Saliendo del sistema...")
                break
            else:
                print("Opción inválida. Intente de nuevo.")
                self._pause()

    iniciar = run


Consola = ConsoleUI
