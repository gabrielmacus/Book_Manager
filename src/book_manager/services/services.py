import datetime
from typing import List, Optional

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    IRepositorio,
    IRepositorioCotizacionDolar,
    IRepositorioStock,
)


class ServicioGenero:
    """Lógica de negocio para la entidad Genero."""

    def __init__(self, repositorio: IRepositorio[Genero]) -> None:
        self._repo = repositorio

    def crear(self, id: int, nombre: str) -> Genero:
        """Crea un nuevo género validando que el nombre no esté duplicado.

        Args:
            id (int): Identificador único del género.
            nombre (str): Nombre del género.

        Returns:
            Genero: El género creado.

        Raises:
            ValueError: Si ya existe un género con el mismo nombre.
        """
        if any(g.nombre.lower() == nombre.strip().lower() for g in self._repo.leer_todos()):
            raise ValueError(f"Ya existe un género con el nombre '{nombre}'.")
        return self._repo.crear(Genero(id, nombre))

    def obtener_todos(self) -> List[Genero]:
        """Retorna todos los géneros registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Genero]:
        """Retorna un género por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def actualizar(self, id: int, nombre: str) -> Genero:
        """Actualiza el nombre de un género existente.

        Args:
            id (int): Identificador del género a modificar.
            nombre (str): Nuevo nombre del género.

        Returns:
            Genero: El género actualizado.

        Raises:
            ValueError: Si no existe el género, o si el nuevo nombre ya está en uso.
        """
        genero = self._repo.leer_por_id(id)
        if genero is None:
            raise ValueError(f"No existe un género con id {id}.")
        duplicado = any(
            g.nombre.lower() == nombre.strip().lower() and g.id != id
            for g in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(f"Ya existe un género con el nombre '{nombre}'.")
        genero.nombre = nombre
        return self._repo.actualizar(genero)

    def eliminar(self, id: int) -> bool:
        """Elimina un género por su id.

        Args:
            id (int): Identificador del género a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioEditorial:
    """Lógica de negocio para la entidad Editorial."""

    def __init__(self, repositorio: IRepositorio[Editorial]) -> None:
        self._repo = repositorio

    def crear(self, id: int, nombre: str) -> Editorial:
        """Crea una nueva editorial validando que el nombre no esté duplicado.

        Args:
            id (int): Identificador único de la editorial.
            nombre (str): Nombre de la editorial.

        Returns:
            Editorial: La editorial creada.

        Raises:
            ValueError: Si ya existe una editorial con el mismo nombre.
        """
        if any(e.nombre.lower() == nombre.strip().lower() for e in self._repo.leer_todos()):
            raise ValueError(f"Ya existe una editorial con el nombre '{nombre}'.")
        return self._repo.crear(Editorial(id, nombre))

    def obtener_todos(self) -> List[Editorial]:
        """Retorna todas las editoriales registradas."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Editorial]:
        """Retorna una editorial por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def actualizar(self, id: int, nombre: str) -> Editorial:
        """Actualiza el nombre de una editorial existente.

        Args:
            id (int): Identificador de la editorial a modificar.
            nombre (str): Nuevo nombre de la editorial.

        Returns:
            Editorial: La editorial actualizada.

        Raises:
            ValueError: Si no existe la editorial, o si el nuevo nombre ya está en uso.
        """
        editorial = self._repo.leer_por_id(id)
        if editorial is None:
            raise ValueError(f"No existe una editorial con id {id}.")
        duplicado = any(
            e.nombre.lower() == nombre.strip().lower() and e.id != id
            for e in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(f"Ya existe una editorial con el nombre '{nombre}'.")
        editorial.nombre = nombre
        return self._repo.actualizar(editorial)

    def eliminar(self, id: int) -> bool:
        """Elimina una editorial por su id.

        Args:
            id (int): Identificador de la editorial a eliminar.

        Returns:
            bool: True si fue eliminada, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioMoneda:
    """Lógica de negocio para la entidad Moneda."""

    def __init__(self, repositorio: IRepositorio[Moneda]) -> None:
        self._repo = repositorio

    def crear(self, id: int, codigo: str, nombre: str) -> Moneda:
        """Crea una nueva moneda validando que el código no esté duplicado.

        Args:
            id (int): Identificador único de la moneda.
            codigo (str): Código ISO de la moneda (ej: 'ARS', 'USD').
            nombre (str): Nombre descriptivo de la moneda.

        Returns:
            Moneda: La moneda creada.

        Raises:
            ValueError: Si ya existe una moneda con el mismo código.
        """
        codigo_normalizado = codigo.strip().upper()
        if any(m.codigo == codigo_normalizado for m in self._repo.leer_todos()):
            raise ValueError(f"Ya existe una moneda con el código '{codigo_normalizado}'.")
        return self._repo.crear(Moneda(id, codigo, nombre))

    def obtener_todos(self) -> List[Moneda]:
        """Retorna todas las monedas registradas."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Moneda]:
        """Retorna una moneda por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def actualizar(self, id: int, codigo: str, nombre: str) -> Moneda:
        """Actualiza los datos de una moneda existente.

        Args:
            id (int): Identificador de la moneda a modificar.
            codigo (str): Nuevo código de la moneda.
            nombre (str): Nuevo nombre de la moneda.

        Returns:
            Moneda: La moneda actualizada.

        Raises:
            ValueError: Si no existe la moneda, o si el código ya está en uso.
        """
        moneda = self._repo.leer_por_id(id)
        if moneda is None:
            raise ValueError(f"No existe una moneda con id {id}.")
        codigo_normalizado = codigo.strip().upper()
        duplicado = any(
            m.codigo == codigo_normalizado and m.id != id
            for m in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(f"Ya existe una moneda con el código '{codigo_normalizado}'.")
        moneda.codigo = codigo
        moneda.nombre = nombre
        return self._repo.actualizar(moneda)

    def eliminar(self, id: int) -> bool:
        """Elimina una moneda por su id.

        Args:
            id (int): Identificador de la moneda a eliminar.

        Returns:
            bool: True si fue eliminada, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioTipoCotizacion:
    """Lógica de negocio para la entidad TipoCotizacion."""

    def __init__(self, repositorio: IRepositorio[TipoCotizacion]) -> None:
        self._repo = repositorio

    def crear(self, id: int, nombre: str) -> TipoCotizacion:
        """Crea un nuevo tipo de cotización validando que el nombre no esté duplicado.

        Args:
            id (int): Identificador único del tipo de cotización.
            nombre (str): Nombre del tipo (ej: 'Oficial', 'Blue', 'MEP').

        Returns:
            TipoCotizacion: El tipo de cotización creado.

        Raises:
            ValueError: Si ya existe un tipo de cotización con el mismo nombre.
        """
        if any(t.nombre.lower() == nombre.strip().lower() for t in self._repo.leer_todos()):
            raise ValueError(f"Ya existe un tipo de cotización con el nombre '{nombre}'.")
        return self._repo.crear(TipoCotizacion(id, nombre))

    def obtener_todos(self) -> List[TipoCotizacion]:
        """Retorna todos los tipos de cotización registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[TipoCotizacion]:
        """Retorna un tipo de cotización por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def actualizar(self, id: int, nombre: str) -> TipoCotizacion:
        """Actualiza el nombre de un tipo de cotización existente.

        Args:
            id (int): Identificador del tipo a modificar.
            nombre (str): Nuevo nombre del tipo de cotización.

        Returns:
            TipoCotizacion: El tipo de cotización actualizado.

        Raises:
            ValueError: Si no existe el tipo, o si el nombre ya está en uso.
        """
        tipo = self._repo.leer_por_id(id)
        if tipo is None:
            raise ValueError(f"No existe un tipo de cotización con id {id}.")
        duplicado = any(
            t.nombre.lower() == nombre.strip().lower() and t.id != id
            for t in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(f"Ya existe un tipo de cotización con el nombre '{nombre}'.")
        tipo.nombre = nombre
        return self._repo.actualizar(tipo)

    def eliminar(self, id: int) -> bool:
        """Elimina un tipo de cotización por su id.

        Args:
            id (int): Identificador del tipo de cotización a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioLibro:
    """Lógica de negocio para la entidad Libro."""

    def __init__(
        self,
        repositorio: IRepositorio[Libro],
        repo_editorial: IRepositorio[Editorial],
        repo_genero: IRepositorio[Genero],
    ) -> None:
        self._repo = repositorio
        self._repo_editorial = repo_editorial
        self._repo_genero = repo_genero

    def crear(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
    ) -> Libro:
        """Crea un nuevo libro con validaciones de integridad referencial.

        Args:
            id (int): Identificador único del libro.
            isbn (str): Código ISBN del libro.
            titulo (str): Título del libro.
            autor (str): Autor del libro.
            editorial_id (int): ID de la editorial asociada.
            genero_id (int): ID del género asociado.

        Returns:
            Libro: El libro creado.

        Raises:
            ValueError: Si el ISBN ya existe, o la editorial/género no existen.
        """
        if any(libro.isbn == isbn.strip() for libro in self._repo.leer_todos()):
            raise ValueError(f"Ya existe un libro con el ISBN '{isbn}'.")
        if self._repo_editorial.leer_por_id(editorial_id) is None:
            raise ValueError(f"No existe una editorial con id {editorial_id}.")
        if self._repo_genero.leer_por_id(genero_id) is None:
            raise ValueError(f"No existe un género con id {genero_id}.")
        return self._repo.crear(Libro(id, isbn, titulo, autor, editorial_id, genero_id))

    def obtener_todos(self) -> List[Libro]:
        """Retorna todos los libros registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Libro]:
        """Retorna un libro por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def actualizar(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
    ) -> Libro:
        """Actualiza los datos de un libro existente.

        Args:
            id (int): Identificador del libro a modificar.
            isbn (str): Nuevo ISBN del libro.
            titulo (str): Nuevo título.
            autor (str): Nuevo autor.
            editorial_id (int): Nuevo ID de editorial.
            genero_id (int): Nuevo ID de género.

        Returns:
            Libro: El libro actualizado.

        Raises:
            ValueError: Si no existe el libro, si el ISBN está duplicado,
                        o si la editorial/género no existen.
        """
        libro = self._repo.leer_por_id(id)
        if libro is None:
            raise ValueError(f"No existe un libro con id {id}.")
        duplicado_isbn = any(
            libro.isbn == isbn.strip() and libro.id != id for libro in self._repo.leer_todos()
        )
        if duplicado_isbn:
            raise ValueError(f"Ya existe un libro con el ISBN '{isbn}'.")
        if self._repo_editorial.leer_por_id(editorial_id) is None:
            raise ValueError(f"No existe una editorial con id {editorial_id}.")
        if self._repo_genero.leer_por_id(genero_id) is None:
            raise ValueError(f"No existe un género con id {genero_id}.")
        libro.isbn = isbn
        libro.titulo = titulo
        libro.autor = autor
        libro.editorial_id = editorial_id
        libro.genero_id = genero_id
        return self._repo.actualizar(libro)

    def eliminar(self, id: int) -> bool:
        """Elimina un libro por su id.

        Args:
            id (int): Identificador del libro a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioPrecio:
    """Lógica de negocio para la entidad Precio."""

    def __init__(
        self,
        repositorio: IRepositorio[Precio],
        repo_libro: IRepositorio[Libro],
        repo_moneda: IRepositorio[Moneda],
    ) -> None:
        self._repo = repositorio
        self._repo_libro = repo_libro
        self._repo_moneda = repo_moneda

    def crear(self, id: int, libro_id: int, moneda_id: int, valor: float) -> Precio:
        """Crea un precio para un libro en una moneda dada.

        Args:
            id (int): Identificador único del precio.
            libro_id (int): ID del libro al que pertenece el precio.
            moneda_id (int): ID de la moneda en que se expresa el precio.
            valor (float): Valor del precio (debe ser mayor a 0).

        Returns:
            Precio: El precio creado.

        Raises:
            ValueError: Si ya existe un precio para esa combinación libro+moneda,
                        o si el libro/moneda no existen.
        """
        if self._repo_libro.leer_por_id(libro_id) is None:
            raise ValueError(f"No existe un libro con id {libro_id}.")
        if self._repo_moneda.leer_por_id(moneda_id) is None:
            raise ValueError(f"No existe una moneda con id {moneda_id}.")
        duplicado = any(
            p.libro_id == libro_id and p.moneda_id == moneda_id
            for p in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe un precio para el libro {libro_id} en la moneda {moneda_id}."
            )
        return self._repo.crear(Precio(id, libro_id, moneda_id, valor))

    def obtener_todos(self) -> List[Precio]:
        """Retorna todos los precios registrados."""
        return self._repo.leer_todos()

    def obtener_por_id(self, id: int) -> Optional[Precio]:
        """Retorna un precio por su id, o None si no existe."""
        return self._repo.leer_por_id(id)

    def obtener_por_libro(self, libro_id: int) -> List[Precio]:
        """Retorna todos los precios asociados a un libro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            List[Precio]: Lista de precios del libro en distintas monedas.
        """
        return [p for p in self._repo.leer_todos() if p.libro_id == libro_id]

    def actualizar(self, id: int, libro_id: int, moneda_id: int, valor: float) -> Precio:
        """Actualiza los datos de un precio existente.

        Args:
            id (int): Identificador del precio a modificar.
            libro_id (int): Nuevo ID de libro.
            moneda_id (int): Nuevo ID de moneda.
            valor (float): Nuevo valor del precio.

        Returns:
            Precio: El precio actualizado.

        Raises:
            ValueError: Si no existe el precio, si el libro/moneda no existen,
                        o si la combinación libro+moneda ya está en uso por otro precio.
        """
        precio = self._repo.leer_por_id(id)
        if precio is None:
            raise ValueError(f"No existe un precio con id {id}.")
        if self._repo_libro.leer_por_id(libro_id) is None:
            raise ValueError(f"No existe un libro con id {libro_id}.")
        if self._repo_moneda.leer_por_id(moneda_id) is None:
            raise ValueError(f"No existe una moneda con id {moneda_id}.")
        duplicado = any(
            p.libro_id == libro_id and p.moneda_id == moneda_id and p.id != id
            for p in self._repo.leer_todos()
        )
        if duplicado:
            raise ValueError(
                f"Ya existe un precio para el libro {libro_id} en la moneda {moneda_id}."
            )
        precio.libro_id = libro_id
        precio.moneda_id = moneda_id
        precio.valor = valor
        return self._repo.actualizar(precio)

    def eliminar(self, id: int) -> bool:
        """Elimina un precio por su id.

        Args:
            id (int): Identificador del precio a eliminar.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(id)


class ServicioStock:
    """Lógica de negocio para la entidad Stock."""

    def __init__(
        self,
        repositorio: IRepositorioStock,
        repo_libro: IRepositorio[Libro],
    ) -> None:
        self._repo = repositorio
        self._repo_libro = repo_libro

    def crear(self, libro_id: int, cantidad: int) -> Stock:
        """Crea un registro de stock para un libro.

        Args:
            libro_id (int): ID del libro.
            cantidad (int): Cantidad inicial en stock (debe ser >= 0).

        Returns:
            Stock: El registro de stock creado.

        Raises:
            ValueError: Si no existe el libro, o si ya tiene stock registrado.
        """
        if self._repo_libro.leer_por_id(libro_id) is None:
            raise ValueError(f"No existe un libro con id {libro_id}.")
        return self._repo.crear(Stock(libro_id, cantidad))

    def obtener_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Retorna el stock de un libro, o None si no existe registro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            Optional[Stock]: El stock del libro, o None.
        """
        return self._repo.leer_por_libro(libro_id)

    def obtener_todos(self) -> List[Stock]:
        """Retorna el stock de todos los libros."""
        return self._repo.leer_todos()

    def actualizar(self, libro_id: int, cantidad: int) -> Stock:
        """Actualiza la cantidad en stock de un libro.

        Args:
            libro_id (int): ID del libro.
            cantidad (int): Nueva cantidad en stock (debe ser >= 0).

        Returns:
            Stock: El stock actualizado.

        Raises:
            ValueError: Si no existe stock para ese libro.
        """
        stock = self._repo.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError(f"No existe stock registrado para el libro {libro_id}.")
        stock.cantidad = cantidad
        return self._repo.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el registro de stock de un libro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            bool: True si fue eliminado, False si no existía.
        """
        return self._repo.eliminar(libro_id)


class ServicioCotizacionDolar:
    """Lógica de negocio para la entidad CotizacionDolar."""

    def __init__(
        self,
        repositorio: IRepositorioCotizacionDolar,
        repo_tipo: IRepositorio[TipoCotizacion],
    ) -> None:
        self._repo = repositorio
        self._repo_tipo = repo_tipo

    def crear(
        self, tipo_id: int, fecha: datetime.date, valor: float
    ) -> CotizacionDolar:
        """Registra una nueva cotización del dólar para un tipo y fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (datetime.date): Fecha de la cotización.
            valor (float): Valor del dólar en esa fecha (debe ser > 0).

        Returns:
            CotizacionDolar: La cotización creada.

        Raises:
            ValueError: Si el tipo no existe, o si ya hay una cotización para
                        ese tipo y fecha.
        """
        if self._repo_tipo.leer_por_id(tipo_id) is None:
            raise ValueError(f"No existe un tipo de cotización con id {tipo_id}.")
        return self._repo.crear(CotizacionDolar(tipo_id, fecha, valor))

    def obtener_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        """Retorna la cotización de un tipo en una fecha específica.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (datetime.date): Fecha de consulta.

        Returns:
            Optional[CotizacionDolar]: La cotización, o None si no existe.
        """
        return self._repo.leer_por_tipo_y_fecha(tipo_id, fecha)

    def obtener_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Retorna el historial de cotizaciones de un tipo, ordenado por fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: Lista de cotizaciones históricas ordenadas por fecha.
        """
        return self._repo.leer_historico_por_tipo(tipo_id)

    def obtener_ultima_cotizacion(self, tipo_id: int) -> Optional[CotizacionDolar]:
        """Retorna la cotización más reciente disponible para un tipo.

        Args:
            tipo_id (int): ID del tipo de cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización más reciente, o None si no hay registros.
        """
        historico = self._repo.leer_historico_por_tipo(tipo_id)
        return historico[-1] if historico else None

    def actualizar(
        self, tipo_id: int, fecha: datetime.date, valor: float
    ) -> CotizacionDolar:
        """Actualiza el valor de una cotización existente.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (datetime.date): Fecha de la cotización a modificar.
            valor (float): Nuevo valor de la cotización.

        Returns:
            CotizacionDolar: La cotización actualizada.

        Raises:
            ValueError: Si no existe la cotización para ese tipo y fecha.
        """
        cotizacion = self._repo.leer_por_tipo_y_fecha(tipo_id, fecha)
        if cotizacion is None:
            raise ValueError(
                f"No existe cotización para el tipo {tipo_id} en la fecha {fecha}."
            )
        cotizacion.valor = valor
        return self._repo.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina una cotización por tipo y fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (datetime.date): Fecha de la cotización a eliminar.

        Returns:
            bool: True si fue eliminada, False si no existía.
        """
        return self._repo.eliminar(tipo_id, fecha)
