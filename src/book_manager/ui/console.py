import sys
import os

# Añade el directorio src al PYTHONPATH si no está ya para permitir importaciones relativas
# if 'book_manager' not in sys.path:
#    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from book_manager.entities.entities import Genero, Editorial, Libro, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar
from book_manager.services.services import Servicios # Asegúrate de que esta clase esté definida

class ConsoleUI:
    def __init__(self, servicios: Servicios):
        self.servicios = servicios

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_input(self, prompt, type=str):
        while True:
            try:
                value = input(prompt)
                if type == int:
                    return int(value)
                elif type == float:
                    return float(value)
                return value
            except ValueError:
                print("Entrada inválida. Por favor, intente de nuevo.")

    def _display_entity_list(self, title, entities):
        self._clear_screen()
        print(f"--- {title} ---")
        if not entities:
            print("No hay registros.")
            return
        for entity in entities:
            print(entity) # Asume que las entidades tienen un __str__ apropiado
        input("Presione Enter para continuar...")

    # --- Gestión de Géneros ---
    def _crear_genero(self):
        self._clear_screen()
        print("--- Crear Género ---")
        nombre = self._get_input("Nombre del género: ")
        genero = Genero(nombre)
        try:
            self.servicios.generos.crear(genero)
            print(f"Género '{nombre}' creado exitosamente.")
        except ValueError as e:
            print(f"Error al crear género: {e}")
        input("Presione Enter para continuar...")

    def _listar_generos(self):
        generos = self.servicios.generos.leer_todos()
        self._display_entity_list("Listado de Géneros", generos)

    def _actualizar_genero(self):
        self._clear_screen()
        print("--- Actualizar Género ---")
        self._listar_generos()
        genero_id = self._get_input("ID del género a actualizar: ", int)
        genero_existente = self.servicios.generos.leer_por_id(genero_id)
        if genero_existente:
            print(f"Género actual: {genero_existente.nombre}")
            nuevo_nombre = self._get_input("Nuevo nombre del género (dejar vacío para no cambiar): ")
            if nuevo_nombre:
                genero_existente.nombre = nuevo_nombre
            try:
                self.servicios.generos.actualizar(genero_existente)
                print(f"Género {genero_id} actualizado exitosamente.")
            except ValueError as e:
                print(f"Error al actualizar género: {e}")
        else:
            print(f"No se encontró género con ID {genero_id}.")
        input("Presione Enter para continuar...")

    def _eliminar_genero(self):
        self._clear_screen()
        print("--- Eliminar Género ---")
        self._listar_generos()
        genero_id = self._get_input("ID del género a eliminar: ", int)
        if self.servicios.generos.eliminar(genero_id):
            print(f"Género {genero_id} eliminado exitosamente.")
        else:
            print(f"No se encontró género con ID {genero_id}.")
        input("Presione Enter para continuar...")

    def manage_generos(self):
        while True:
            self._clear_screen()
            print("\n--- Gestión de Géneros ---")
            print("1. Crear Género")
            print("2. Listar Géneros")
            print("3. Actualizar Género")
            print("4. Eliminar Género")
            print("0. Volver al Menú Principal")
            choice = self._get_input("Seleccione una opción: ", int)

            if choice == 1:
                self._crear_genero()
            elif choice == 2:
                self._listar_generos()
            elif choice == 3:
                self._actualizar_genero()
            elif choice == 4:
                self._eliminar_genero()
            elif choice == 0:
                break
            else:
                print("Opción inválida. Intente de nuevo.")

    # --- Gestión de Editoriales ---
    # Implementar métodos _crear_editorial, _listar_editoriales, _actualizar_editorial, _eliminar_editorial
    # siguiendo el patrón de Generos. Aquí se muestra una versión simplificada.

    def _crear_editorial(self):
        self._clear_screen()
        print("--- Crear Editorial ---")
        nombre = self._get_input("Nombre de la editorial: ")
        pais = self._get_input("País de la editorial: ")
        editorial = Editorial(nombre, pais)
        try:
            self.servicios.editoriales.crear(editorial)
            print(f"Editorial '{nombre}' creada exitosamente.")
        except ValueError as e:
            print(f"Error al crear editorial: {e}")
        input("Presione Enter para continuar...")

    def _listar_editoriales(self):
        editoriales = self.servicios.editoriales.leer_todos()
        self._display_entity_list("Listado de Editoriales", editoriales)

    def _actualizar_editorial(self):
        self._clear_screen()
        print("--- Actualizar Editorial ---")
        self._listar_editoriales()
        editorial_id = self._get_input("ID de la editorial a actualizar: ", int)
        editorial_existente = self.servicios.editoriales.leer_por_id(editorial_id)
        if editorial_existente:
            print(f"Editorial actual: {editorial_existente.nombre} ({editorial_existente.pais})")
            nuevo_nombre = self._get_input("Nuevo nombre de la editorial (dejar vacío para no cambiar): ")
            nuevo_pais = self._get_input("Nuevo país de la editorial (dejar vacío para no cambiar): ")
            if nuevo_nombre:
                editorial_existente.nombre = nuevo_nombre
            if nuevo_pais:
                editorial_existente.pais = nuevo_pais
            try:
                self.servicios.editoriales.actualizar(editorial_existente)
                print(f"Editorial {editorial_id} actualizada exitosamente.")
            except ValueError as e:
                print(f"Error al actualizar editorial: {e}")
        else:
            print(f"No se encontró editorial con ID {editorial_id}.")
        input("Presione Enter para continuar...")

    def _eliminar_editorial(self):
        self._clear_screen()
        print("--- Eliminar Editorial ---")
        self._listar_editoriales()
        editorial_id = self._get_input("ID de la editorial a eliminar: ", int)
        if self.servicios.editoriales.eliminar(editorial_id):
            print(f"Editorial {editorial_id} eliminada exitosamente.")
        else:
            print(f"No se encontró editorial con ID {editorial_id}.")
        input("Presione Enter para continuar...")


    def manage_editoriales(self):
        while True:
            self._clear_screen()
            print("\n--- Gestión de Editoriales ---")
            print("1. Crear Editorial")
            print("2. Listar Editoriales")
            print("3. Actualizar Editorial")
            print("4. Eliminar Editorial")
            print("0. Volver al Menú Principal")
            choice = self._get_input("Seleccione una opción: ", int)

            if choice == 1:
                self._crear_editorial()
            elif choice == 2:
                self._listar_editoriales()
            elif choice == 3:
                self._actualizar_editorial()
            elif choice == 4:
                self._eliminar_editorial()
            elif choice == 0:
                break
            else:
                print("Opción inválida. Intente de nuevo.")

    # --- Implementar métodos manage_ para las otras entidades (Libros, Monedas, etc.) ---
    # def manage_libros(self):
    #    # ... implementación para CRUD de Libros ...
    #    pass

    # def manage_monedas(self):
    #    # ... implementación para CRUD de Monedas ...
    #    pass

    # def manage_tipos_cotizacion(self):
    #    # ... implementación para CRUD de TipoCotizacion ...
    #    pass

    # def manage_precios(self):
    #    # ... implementación para CRUD de Precios ...
    #    pass

    # def manage_stock(self):
    #    # ... implementación para CRUD de Stock ...
    #    pass

    # def manage_cotizaciones_dolar(self):
    #    # ... implementación para CRUD de CotizacionDolar ...
    #    pass


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
            choice = self._get_input("Seleccione una opción: ", int)

            if choice == 1:
                self.manage_generos()
            elif choice == 2:
                self.manage_editoriales()
            elif choice == 3:
                print("Funcionalidad no implementada aún para Libros.")
                input("Presione Enter para continuar...")
                # self.manage_libros()
            elif choice == 4:
                print("Funcionalidad no implementada aún para Monedas.")
                input("Presione Enter para continuar...")
                # self.manage_monedas()
            elif choice == 5:
                print("Funcionalidad no implementada aún para Tipos de Cotización.")
                input("Presione Enter para continuar...")
                # self.manage_tipos_cotizacion()
            elif choice == 6:
                print("Funcionalidad no implementada aún para Precios.")
                input("Presione Enter para continuar...")
                # self.manage_precios()
            elif choice == 7:
                print("Funcionalidad no implementada aún para Stock.")
                input("Presione Enter para continuar...")
                # self.manage_stock()
            elif choice == 8:
                print("Funcionalidad no implementada aún para Cotizaciones Dólar.")
                input("Presione Enter para continuar...")
                # self.manage_cotizaciones_dolar()
            elif choice == 0:
                print("Saliendo del sistema...")
                break
            else:
                print("Opción inválida. Intente de nuevo.")
                input("Presione Enter para continuar...")

if __name__ == '__main__':
    # Este bloque solo se ejecuta si console.py se ejecuta directamente
    # En un entorno de Colab, es probable que se importe y se use desde main.py
    try:
        # Crear una instancia de Servicios (asegúrate de que los repositorios estén implementados)
        # Esto es un placeholder; la inicialización real de servicios debería ser robusta.
        from book_manager.repositories.repositories import RepositorioGenerosMemoria, RepositorioEditorialesMemoria
        # ... importar otros repositorios

        servicios = Servicios(
            generos_repo=RepositorioGenerosMemoria(),
            editoriales_repo=RepositorioEditorialesMemoria(),
            # ... pasar otras instancias de repositorio
        )

        ui = ConsoleUI(servicios)
        ui.run()
    except ImportError as e:
        print(f"Error de importación: {e}. Asegúrate de que las entidades y servicios estén definidos.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
