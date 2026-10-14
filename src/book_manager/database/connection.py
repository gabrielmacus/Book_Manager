"""Conexión a la base de datos con SQLAlchemy."""
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

RAIZ_PROYECTO = Path(__file__).resolve().parents[3]


class ConexionDB:
    """Administra el engine y las sesiones de SQLAlchemy."""

    def __init__(self, url: Optional[str] = None) -> None:
        """Crea el engine a partir de la URL indicada o de DATABASE_URL.

        Las variables se leen de .env y .env.local en la raíz del proyecto,
        sin pisar las que ya existen en el entorno (por ejemplo, en Colab).

        Args:
            url (Optional[str]): URL de conexión. Si es None, se usa la
                variable de entorno DATABASE_URL.

        Raises:
            ValueError: Si no se indica una URL y falta DATABASE_URL.
        """
        load_dotenv(RAIZ_PROYECTO / ".env")
        load_dotenv(RAIZ_PROYECTO / ".env.local")
        url = url or os.getenv("DATABASE_URL")
        if not url:
            raise ValueError("Falta la variable de entorno DATABASE_URL.")
        self._engine = create_engine(url)
        self._sesiones = sessionmaker(bind=self._engine)

    @property
    def engine(self) -> Engine:
        """Engine de SQLAlchemy asociado a la base de datos."""
        return self._engine

    def nueva_sesion(self) -> Session:
        """Devuelve una nueva sesión para operar con la base de datos."""
        return self._sesiones()

    @contextmanager
    def transaccion(self) -> Iterator[Session]:
        """Abre una sesión y la confirma o revierte al salir del bloque.

        Si el bloque termina bien se hace commit; si lanza una excepción se
        hace rollback y la excepción se propaga. La sesión siempre se cierra.

        Yields:
            Session: Sesión para operar dentro de la transacción.
        """
        sesion = self.nueva_sesion()
        try:
            yield sesion
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()

    def cerrar(self) -> None:
        """Libera las conexiones abiertas del engine."""
        self._engine.dispose()
