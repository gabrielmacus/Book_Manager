"""Modelos SQLAlchemy con las tablas del sistema y sus relaciones."""
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from book_manager.database.connection import ConexionDB


class Base(DeclarativeBase):
    """Clase base declarativa de todos los modelos."""


class GeneroModel(Base):
    """Tabla de géneros literarios."""

    __tablename__ = "generos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    nombre: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )

    libros: Mapped[list["LibroModel"]] = relationship(back_populates="genero")


class EditorialModel(Base):
    """Tabla de editoriales."""

    __tablename__ = "editoriales"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    nombre: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )

    libros: Mapped[list["LibroModel"]] = relationship(
        back_populates="editorial"
    )


class MonedaModel(Base):
    """Tabla de monedas."""

    __tablename__ = "monedas"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    codigo: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    precios: Mapped[list["PrecioModel"]] = relationship(
        back_populates="moneda"
    )


class TipoCotizacionModel(Base):
    """Tabla de tipos de cotización del dólar."""

    __tablename__ = "tipos_cotizacion"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    nombre: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    cotizaciones: Mapped[list["CotizacionDolarModel"]] = relationship(
        back_populates="tipo"
    )


class LibroModel(Base):
    """Tabla de libros."""

    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    isbn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    autor: Mapped[str] = mapped_column(String(150), nullable=False)
    editorial_id: Mapped[int] = mapped_column(ForeignKey("editoriales.id"))
    genero_id: Mapped[int] = mapped_column(ForeignKey("generos.id"))

    editorial: Mapped["EditorialModel"] = relationship(back_populates="libros")
    genero: Mapped["GeneroModel"] = relationship(back_populates="libros")
    precios: Mapped[list["PrecioModel"]] = relationship(back_populates="libro")
    stock: Mapped["StockModel | None"] = relationship(
        back_populates="libro", uselist=False
    )
    precios_web: Mapped[list["PrecioWebModel"]] = relationship(
        back_populates="libro"
    )


class PrecioModel(Base):
    """Tabla de precios de un libro en una moneda."""

    __tablename__ = "precios"
    __table_args__ = (UniqueConstraint("libro_id", "moneda_id"),)

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=False
    )
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id"))
    moneda_id: Mapped[int] = mapped_column(ForeignKey("monedas.id"))
    valor: Mapped[float] = mapped_column(Float)

    libro: Mapped["LibroModel"] = relationship(back_populates="precios")
    moneda: Mapped["MonedaModel"] = relationship(back_populates="precios")


class StockModel(Base):
    """Tabla de stock: un registro por libro."""

    __tablename__ = "stock"

    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id"), primary_key=True
    )
    cantidad: Mapped[int] = mapped_column(Integer)

    libro: Mapped["LibroModel"] = relationship(back_populates="stock")


class CotizacionDolarModel(Base):
    """Tabla de cotizaciones del dólar por tipo y fecha."""

    __tablename__ = "cotizaciones"

    tipo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_cotizacion.id"), primary_key=True
    )
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    valor: Mapped[float] = mapped_column(Float)

    tipo: Mapped["TipoCotizacionModel"] = relationship(
        back_populates="cotizaciones"
    )


class PrecioWebModel(Base):
    """Tabla de precios de libros obtenidos por scraping de Cúspide."""

    __tablename__ = "precios_web"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id"))
    posicion: Mapped[int] = mapped_column(Integer)
    titulo: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(500))
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    precio: Mapped[float] = mapped_column(Float)
    precio_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    imagen_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    formas_pago: Mapped[str] = mapped_column(Text, default="")
    descripcion: Mapped[str] = mapped_column(Text, default="")
    especificaciones: Mapped[str] = mapped_column(Text, default="")
    fecha_extraccion: Mapped[datetime] = mapped_column(DateTime)

    libro: Mapped["LibroModel"] = relationship(back_populates="precios_web")


class AuditoriaModel(Base):
    """Tabla de auditoría de operaciones del sistema."""

    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    detalles: Mapped[str] = mapped_column(Text, default="")


def crear_tablas(conexion: ConexionDB) -> None:
    """Crea en la base todas las tablas que todavía no existan.

    Args:
        conexion: Conexión a la base de datos sobre la que se crean las tablas.
    """
    Base.metadata.create_all(conexion.engine)
