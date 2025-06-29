from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ARRAY, BigInteger, ForeignKey, Numeric, JSON, Date
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from bot_instance import SQL_URL_RC

engine = create_async_engine(url=SQL_URL_RC, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)


class Resume(Base):
    __tablename__ = "resume"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    plain = Column(String, default='')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)