import enum
import asyncio

from sqlalchemy.engine import URL
from urllib.parse import quote_plus
from sqlalchemy.types import JSON, Enum

from sqlalchemy import ForeignKey, select
from typing import Dict, Any, Optional, List, Literal

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, joinedload


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
    file: Mapped["File"] = relationship(back_populates = "batches")


class AsyncSessionManager:

    def __init__(self, connection_url: str, schema: str):
        self.engine = create_async_engine(connection_url, connect_args = {"server_settings": {"search_path": schema}})
        self.session = async_sessionmaker(self.engine, expire_on_commit = False)

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *excinfo):
        await self.engine.dispose()

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def create_file(self, id: str, name: str, content: Dict[str, Any], status: Literal["completed", "failed", "in_progress"]):
        async with self.session() as session:
            file = File(
                id = id, 
                name = name, 
                content = content, 
                status = status
            )
            session.add(file)
            await session.commit()
        return file

    async def read_file(self, id: str):
        async with self.session() as session:
            # results = await session.execute(select(File).where(File.id == id))
            # file = results.scalars().one()

            # results = await session.execute(select(File).where(File.id == id))
            # file = results.scalars().all()

            # results = await session.execute(select(File).where(File.id == id))
            # file = results.scalar()

            file = await session.get(File, id, options = [joinedload(File.batches)])
        return file

    async def update_file(self, file: File, **kwargs):
        async with self.session() as session:
            for property, value in kwargs.items():
                setattr(file, property, value)
            session.add(file)
            await session.commit()
        return file  

    async def create_batch(self, id: str, status: Literal["completed", "failed", "in_progress"], results: Dict[str, Any], file: File):
        async with self.session() as session:
            batch = Batch(
                id = id,
                status = status,
                results = results,
                file = file
            )
            session.add(batch)
            await session.commit()
        return batch

    async def read_batch(self, id: str):
        async with self.session() as session:
            batch = await session.get(Batch, id, options = [joinedload(Batch.file)])
        return batch

    async def update_batch(self, batch: Batch, **kwargs):
        async with self.session() as session:
            for property, value in kwargs.items():
                setattr(batch, property, value)
            session.add(batch)
            await session.commit()
        return batch
    

async def main(connection_url: str, schema: str):
    async with AsyncSessionManager(connection_url = connection_url, schema = schema) as session:
        # Create file
        await session.create_file(id = "1", name = "file 1", content = {"content": "1"}, status = "completed")
        await session.create_file(id = "2", name = "file 2", content = {"content": "2"}, status = "completed")

        # # Read file
        # file = await session.read_file(id = "1")
        # for batch in file.batches:
        #     print(batch.results)
        # file = await session.read_file(id = "2")
        

        # Update file
        # updated_file = await session.update_file(file, name = "file 1 update")

        # Create batch
        # file = await session.read_file(id = "1")
        # batch = await session.create_batch(id = "1", status = "completed", results = {"results": "1"}, file = file)

        # Read batch
        # batch = await session.read_batch(id = "1")
        # print(batch.file.name)

        # Update batch
        # updated_batch = await session.update_batch(batch, file = file)


if __name__ == "__main__":
    connection_url = URL.create(
        drivername = "postgresql+asyncpg",
        username = "postgres",
        password = quote_plus("postgres"),
        host = "localhost",
        port = 5432,
        database = "postgres"
    )
    schema = "mlops"
    asyncio.run(main(connection_url = connection_url, schema = schema))