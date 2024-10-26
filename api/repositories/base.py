from typing import TypeVar, Generic, Type

from sqlalchemy import delete, insert, select, update

from api.database import async_session_maker

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: Type[T] = None
    
    async def insert(self, **kwargs) -> T:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**kwargs).returning(self.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().one()
    
    async def update(
            self,
            filter_args: dict,
            **kwargs,
    ) -> T:
        async with async_session_maker() as session:
            stmt = update(self.model).filter_by(**filter_args).values(**kwargs).returning(self.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().one()
    
    async def delete(self, **kwargs) -> T:
        async with async_session_maker() as session:
            stmt = delete(self.model).filter_by(**kwargs).returning(self.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalars().one()
    
    async def get_one_or_none(
            self,
            sorting_filters: list = [],
            **kwargs,
    ) -> T:
        async with async_session_maker() as session:
            query = select(self.model).filter_by(**kwargs).order_by(*sorting_filters)
            result = await session.execute(query)
            return result.scalars().one_or_none()
    
    async def get_all(
            self,
            sorting_filters: list = [],
            limit: int = None,
            **kwargs,
    ) -> list[T]:
        async with async_session_maker() as session:
            query = select(self.model).filter_by(**kwargs).order_by(*sorting_filters).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
