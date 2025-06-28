import enum
import asyncio

from sqlalchemy import ForeignKey
from sqlalchemy.engine import URL
from sqlalchemy.types import JSON, Enum

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Status(enum.Enum):
    completed = "completed"
    failed = "failed"
    in_progress = "in_progress"


class Base(DeclarativeBase):
    type_annotation_map = {
        Dict[str, Any]: JSON
    }


class File(Base):
    __tablename__ = "file"

    id: Mapped[str] = mapped_column(primary_key = True)
    name: Mapped[str]
    content: Mapped[Dict[str, Any]]
    status: Mapped[str] = mapped_column(Enum(Status, name = "status"))
    batches: Mapped[List["Batch"]] = relationship(back_populates = "file", cascade = "all, delete-orphan")


class Batch(Base):
    __tablename__ = "batch"

    id: Mapped[str] = mapped_column(primary_key = True)
    status: Mapped[str] = mapped_column(Enum(Status, name = "status"))
    results: Mapped[Optional[Dict[str, Any]]]
    file_id: Mapped[str] = mapped_column(ForeignKey("file.id"))
    file: Mapped["File"] = relationship(back_populates = "files")


async def main(connection_url: str):
    engine = create_async_engine(connection_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    connection_url = URL.create(
        drivername = "postgresql+asyncpg",
        username = "postgres",
        password = "postgres",
        host = "localhost",
        port = 5432,
        database = "postgres"
    )
    asyncio.run(main(connection_url = connection_url))
