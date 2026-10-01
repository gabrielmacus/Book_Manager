import datetime
import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

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
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)


class Servicios:
    def __init__(self, ruta_csv=None):
        if ruta_csv is None:
            ruta_csv = Path(__file__).resolve().parent.parent / "migrations" / "csv"

        repo_genero = RepositorioGeneroCsv(ruta_csv / "generos.csv")
        repo_editorial = RepositorioEditorialCsv(ruta_csv / "editoriales.csv")
        repo_moneda = RepositorioMonedaCsv(ruta_csv / "monedas.csv")
        repo_tipo = RepositorioTipoCotizacionCsv(ruta_csv / "tipos_cotizacion.csv")
        repo_libro = RepositorioLibroCsv(ruta_csv / "libros.csv")
        repo_precio = RepositorioPrecioCsv(ruta_csv / "precios.csv")
        repo_stock = RepositorioStockCsv(ruta_csv / "stock.csv")
        repo_cotizacion = RepositorioCotizacionDolarCsv(ruta_csv / "cotizaciones.csv")

        self.generos = ServicioGenero(repo_genero)
        self.editoriales = ServicioEditorial(repo_editorial)
        self.monedas = ServicioMoneda(repo_moneda)
        self.tipos = ServicioTipoCotizacion(repo_tipo)
        self.libros = ServicioLibro(repo_libro, repo_editorial, repo_genero)
        self.precios = ServicioPrecio(repo_precio, repo_libro, repo_moneda)
        self.stock = ServicioStock(repo_stock, repo_libro)
        self.cotizaciones = ServicioCotizacionDolar(repo_cotizacion, repo_tipo)


class ConsoleUI:
    def __init__(self, servicios=None):
        if servicios is None:
            servicios = Servicios()
        self.servicios = servicios

    def _clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def _get_input(self, prompt, tipo=str):
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

    def _pause(self):
        input("\nPresione Enter para continuar...")

    def _display_list(self, titulo, items, formateador):
        self._clear_screen()
        print(f"--- {titulo} ---")
        if not items:
            print("No hay registros.")
        else:
            for item in items:
                print(formateador(item))
        self._pause()

    def _crear_genero(self):
        self._clear_screen()
        print("--- Crear Género ---")
        id = self._get_input("ID: ", int)
        nombre = self._get_input("Nombre del género: ")
        try:
            genero = self.servicios.generos.crear(id, nombre)
            print(f"Género creado: ID {genero.id} - {genero.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_generos(self):
        self._display_list(
            "Listado de Géneros",
            self.servicios.generos.obtener_todos(),
            lambda g: f"ID: {g.id} | Nombre: {g.nombre}",
        )

    def _buscar_genero(self):
        self._clear_screen()
        print("--- Buscar Género por ID ---")
        id = self._get_input("ID a buscar: ", int)
        genero = self.servicios.generos.obtener_por_id(id)
        if genero:
            print(f"ID: {genero.id} | Nombre: {genero.nombre}")
        else:
            print(f"No se encontró un género con ID {id}.")
        self._pause()

    def _actualizar_genero(self):
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

    def _eliminar_genero(self):
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

    def manage_generos(self):
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

    def _crear_editorial(self):
        self._clear_screen()
        print("--- Crear Editorial ---")
        id = self._get_input("ID: ", int)
        nombre = self._get_input("Nombre de la editorial: ")
        try:
            editorial = self.servicios.editoriales.crear(id, nombre)
            print(f"Editorial creada: ID {editorial.id} - {editorial.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_editoriales(self):
        self._display_list(
            "Listado de Editoriales",
            self.servicios.editoriales.obtener_todos(),
            lambda e: f"ID: {e.id} | Nombre: {e.nombre}",
        )

    def _buscar_editorial(self):
        self._clear_screen()
        print("--- Buscar Editorial por ID ---")
        id = self._get_input("ID a buscar: ", int)
        editorial = self.servicios.editoriales.obtener_por_id(id)
        if editorial:
            print(f"ID: {editorial.id} | Nombre: {editorial.nombre}")
        else:
            print(f"No se encontró una editorial con ID {id}.")
        self._pause()

    def _actualizar_editorial(self):
        self._clear_screen()
        print("--- Actualizar Editorial ---")
        id = self._get_input("ID de la editorial a actualizar: ", int)
        nuevo_nombre = self._get_input("Nuevo nombre: ")
        try:
            editorial = self.servicios.editoriales.actualizar(id, nuevo_nombre)
            print(f"Editorial actualizada: ID {editorial.id} - {editorial.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_editorial(self):
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

    def manage_editoriales(self):
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

    def _crear_libro(self):
        self._clear_screen()
        print("--- Crear Libro ---")
        id = self._get_input("ID: ", int)
        isbn = self._get_input("ISBN: ")
        titulo = self._get_input("Título: ")
        autor = self._get_input("Autor: ")
        editorial_id = self._get_input("ID Editorial: ", int)
        genero_id = self._get_input("ID Género: ", int)
        try:
            libro = self.servicios.libros.crear(id, isbn, titulo, autor, editorial_id, genero_id)
            print(f"Libro creado: ID {libro.id} - '{libro.titulo}' de {libro.autor}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_libros(self):
        self._display_list(
            "Listado de Libros",
            self.servicios.libros.obtener_todos(),
            lambda l: f"ID: {l.id} | ISBN: {l.isbn} | Título: {l.titulo} | Autor: {l.autor} | Editorial: {l.editorial_id} | Género: {l.genero_id}",
        )

    def _buscar_libro(self):
        self._clear_screen()
        print("--- Buscar Libro por ID ---")
        id = self._get_input("ID a buscar: ", int)
        libro = self.servicios.libros.obtener_por_id(id)
        if libro:
            print(f"ID: {libro.id} | ISBN: {libro.isbn} | Título: {libro.titulo} | Autor: {libro.autor} | Editorial: {libro.editorial_id} | Género: {libro.genero_id}")
        else:
            print(f"No se encontró un libro con ID {id}.")
        self._pause()

    def _actualizar_libro(self):
        self._clear_screen()
        print("--- Actualizar Libro ---")
        id = self._get_input("ID a actualizar: ", int)
        isbn = self._get_input("Nuevo ISBN: ")
        titulo = self._get_input("Nuevo título: ")
        autor = self._get_input("Nuevo autor: ")
        editorial_id = self._get_input("Nuevo ID Editorial: ", int)
        genero_id = self._get_input("Nuevo ID Género: ", int)
        try:
            libro = self.servicios.libros.actualizar(id, isbn, titulo, autor, editorial_id, genero_id)
            print(f"Libro actualizado: ID {libro.id} - '{libro.titulo}'")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_libro(self):
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

    def manage_libros(self):
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

    def _crear_moneda(self):
        self._clear_screen()
        print("--- Crear Moneda ---")
        id = self._get_input("ID: ", int)
        codigo = self._get_input("Código (ej: ARS, USD): ")
        nombre = self._get_input("Nombre: ")
        try:
            moneda = self.servicios.monedas.crear(id, codigo, nombre)
            print(f"Moneda creada: ID {moneda.id} - {moneda.codigo} ({moneda.nombre})")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_monedas(self):
        self._display_list(
            "Listado de Monedas",
            self.servicios.monedas.obtener_todos(),
            lambda m: f"ID: {m.id} | Código: {m.codigo} | Nombre: {m.nombre}",
        )

    def _buscar_moneda(self):
        self._clear_screen()
        print("--- Buscar Moneda por ID ---")
        id = self._get_input("ID a buscar: ", int)
        moneda = self.servicios.monedas.obtener_por_id(id)
        if moneda:
            print(f"ID: {moneda.id} | Código: {moneda.codigo} | Nombre: {moneda.nombre}")
        else:
            print(f"No se encontró una moneda con ID {id}.")
        self._pause()

    def _actualizar_moneda(self):
        self._clear_screen()
        print("--- Actualizar Moneda ---")
        id = self._get_input("ID a actualizar: ", int)
        codigo = self._get_input("Nuevo código: ")
        nombre = self._get_input("Nuevo nombre: ")
        try:
            moneda = self.servicios.monedas.actualizar(id, codigo, nombre)
            print(f"Moneda actualizada: ID {moneda.id} - {moneda.codigo} ({moneda.nombre})")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_moneda(self):
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

    def manage_monedas(self):
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

    def _crear_tipo_cotizacion(self):
        self._clear_screen()
        print("--- Crear Tipo de Cotización ---")
        id = self._get_input("ID: ", int)
        nombre = self._get_input("Nombre (ej: Oficial, Blue): ")
        try:
            tipo = self.servicios.tipos.crear(id, nombre)
            print(f"Tipo creado: ID {tipo.id} - {tipo.nombre}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_tipos_cotizacion(self):
        self._display_list(
            "Listado de Tipos de Cotización",
            self.servicios.tipos.obtener_todos(),
            lambda t: f"ID: {t.id} | Nombre: {t.nombre}",
        )

    def _buscar_tipo_cotizacion(self):
        self._clear_screen()
        print("--- Buscar Tipo de Cotización por ID ---")
        id = self._get_input("ID a buscar: ", int)
        tipo = self.servicios.tipos.obtener_por_id(id)
        if tipo:
            print(f"ID: {tipo.id} | Nombre: {tipo.nombre}")
        else:
            print(f"No se encontró un tipo de cotización con ID {id}.")
        self._pause()

    def _actualizar_tipo_cotizacion(self):
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

    def _eliminar_tipo_cotizacion(self):
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

    def manage_tipos_cotizacion(self):
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

    def _crear_precio(self):
        self._clear_screen()
        print("--- Crear Precio ---")
        id = self._get_input("ID: ", int)
        libro_id = self._get_input("ID Libro: ", int)
        moneda_id = self._get_input("ID Moneda: ", int)
        valor = self._get_input("Valor: ", float)
        try:
            precio = self.servicios.precios.crear(id, libro_id, moneda_id, valor)
            print(f"Precio creado: ID {precio.id} | Libro {precio.libro_id} | Moneda {precio.moneda_id} | Valor: {precio.valor}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_precios(self):
        self._display_list(
            "Listado de Precios",
            self.servicios.precios.obtener_todos(),
            lambda p: f"ID: {p.id} | Libro ID: {p.libro_id} | Moneda ID: {p.moneda_id} | Valor: {p.valor}",
        )

    def _buscar_precio(self):
        self._clear_screen()
        print("--- Buscar Precio por ID ---")
        id = self._get_input("ID a buscar: ", int)
        precio = self.servicios.precios.obtener_por_id(id)
        if precio:
            print(f"ID: {precio.id} | Libro ID: {precio.libro_id} | Moneda ID: {precio.moneda_id} | Valor: {precio.valor}")
        else:
            print(f"No se encontró un precio con ID {id}.")
        self._pause()

    def _listar_precios_por_libro(self):
        self._clear_screen()
        print("--- Listar Precios por Libro ---")
        libro_id = self._get_input("ID Libro: ", int)
        precios = self.servicios.precios.obtener_por_libro(libro_id)
        self._display_list(
            f"Precios del Libro {libro_id}",
            precios,
            lambda p: f"ID: {p.id} | Moneda ID: {p.moneda_id} | Valor: {p.valor}",
        )

    def _actualizar_precio(self):
        self._clear_screen()
        print("--- Actualizar Precio ---")
        id = self._get_input("ID a actualizar: ", int)
        libro_id = self._get_input("Nuevo ID Libro: ", int)
        moneda_id = self._get_input("Nuevo ID Moneda: ", int)
        valor = self._get_input("Nuevo valor: ", float)
        try:
            precio = self.servicios.precios.actualizar(id, libro_id, moneda_id, valor)
            print(f"Precio actualizado: ID {precio.id} | Valor: {precio.valor}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_precio(self):
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

    def manage_precios(self):
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

    def _crear_stock(self):
        self._clear_screen()
        print("--- Registrar Stock ---")
        libro_id = self._get_input("ID Libro: ", int)
        cantidad = self._get_input("Cantidad: ", int)
        try:
            stock = self.servicios.stock.crear(libro_id, cantidad)
            print(f"Stock registrado: Libro {stock.libro_id} | Cantidad: {stock.cantidad}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _listar_stock(self):
        self._display_list(
            "Listado de Stock",
            self.servicios.stock.obtener_todos(),
            lambda s: f"Libro ID: {s.libro_id} | Cantidad: {s.cantidad}",
        )

    def _buscar_stock(self):
        self._clear_screen()
        print("--- Buscar Stock por ID de Libro ---")
        libro_id = self._get_input("ID Libro a consultar: ", int)
        stock = self.servicios.stock.obtener_por_libro(libro_id)
        if stock:
            print(f"Libro ID: {stock.libro_id} | Cantidad: {stock.cantidad}")
        else:
            print(f"No se encontró stock registrado para el libro {libro_id}.")
        self._pause()

    def _actualizar_stock(self):
        self._clear_screen()
        print("--- Actualizar Stock ---")
        libro_id = self._get_input("ID Libro a actualizar: ", int)
        cantidad = self._get_input("Nueva cantidad: ", int)
        try:
            stock = self.servicios.stock.actualizar(libro_id, cantidad)
            print(f"Stock actualizado: Libro {stock.libro_id} | Cantidad: {stock.cantidad}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_stock(self):
        self._clear_screen()
        print("--- Eliminar Stock ---")
        libro_id = self._get_input("ID Libro a eliminar stock: ", int)
        try:
            if self.servicios.stock.eliminar(libro_id):
                print(f"Stock del libro {libro_id} eliminado exitosamente.")
            else:
                print(f"No se encontró stock registrado para el libro {libro_id}.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def manage_stock(self):
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

    def _crear_cotizacion(self):
        self._clear_screen()
        print("--- Registrar Cotización de Dólar ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        valor = self._get_input("Valor: ", float)
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            cotiz = self.servicios.cotizaciones.crear(tipo_id, fecha, valor)
            print(f"Cotización registrada: Tipo {cotiz.tipo_id} | Fecha {cotiz.fecha} | Valor: {cotiz.valor}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _consultar_cotizacion(self):
        self._clear_screen()
        print("--- Consultar Cotización por Tipo y Fecha ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            cotiz = self.servicios.cotizaciones.obtener_por_tipo_y_fecha(tipo_id, fecha)
            if cotiz:
                print(f"Tipo ID: {cotiz.tipo_id} | Fecha: {cotiz.fecha} | Valor: {cotiz.valor}")
            else:
                print("No se encontró cotización para ese tipo y fecha.")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _historico_cotizaciones(self):
        self._clear_screen()
        print("--- Histórico de Cotizaciones por Tipo ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        historico = self.servicios.cotizaciones.obtener_historico_por_tipo(tipo_id)
        self._display_list(
            f"Histórico de Cotizaciones - Tipo {tipo_id}",
            historico,
            lambda c: f"Fecha: {c.fecha} | Valor: {c.valor}",
        )

    def _ultima_cotizacion(self):
        self._clear_screen()
        print("--- Última Cotización de un Tipo ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        cotiz = self.servicios.cotizaciones.obtener_ultima_cotizacion(tipo_id)
        if cotiz:
            print(f"Última cotización -> Fecha: {cotiz.fecha} | Valor: {cotiz.valor}")
        else:
            print("No hay cotizaciones registradas para ese tipo.")
        self._pause()

    def _actualizar_cotizacion(self):
        self._clear_screen()
        print("--- Actualizar Cotización ---")
        tipo_id = self._get_input("ID Tipo Cotización: ", int)
        fecha_str = self._get_input("Fecha (AAAA-MM-DD): ")
        valor = self._get_input("Nuevo valor: ", float)
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            cotiz = self.servicios.cotizaciones.actualizar(tipo_id, fecha, valor)
            print(f"Cotización actualizada: Tipo {cotiz.tipo_id} | Fecha {cotiz.fecha} | Valor: {cotiz.valor}")
        except ValueError as e:
            print(f"Error: {e}")
        self._pause()

    def _eliminar_cotizacion(self):
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

    def manage_cotizaciones_dolar(self):
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

    def run(self):
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
            elif opcion == 0:
                print("Saliendo del sistema...")
                break
            else:
                print("Opción inválida. Intente de nuevo.")
                self._pause()

    iniciar = run


Consola = ConsoleUI
