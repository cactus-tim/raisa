from sqlalchemy import select, desc, distinct, and_

from database.models import User, Resume, async_session
from errors.errors import *
from errors.handlers import db_error_handler


@db_error_handler
async def get_user(tg_id: int) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == tg_id))
        if user:
            return user
        else:
            raise Error404


@db_error_handler
async def create_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await get_user(tg_id)
        if not user:
            user_data = User(id=tg_id)
            session.add(user_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def add_reference(plain: str) -> None:
    async with async_session() as session:
        resume_data = Resume(plain=plain)
        session.add(resume_data)
        await session.commit()


@db_error_handler
async def create_extended_prompt() -> str:
    async with async_session() as session:
        plains = await session.execute(select(Resume.plain))
        extended_prompt = ("Используй эти примеры написанных вакансий как пример, основывайся на нем"
                           + '\n\n\n'.join(plains.scalars().all())
                           + "Теперь начни диалог с пользователем и воплняй свою задачу\n"
                           + "В своих ответах используй только html разметку для текста, но только описанные ниже теги,"
                             " никакие больше использовать нельзя, это теги совместимые с telegram:"
                             "<b>…</b>, <strong>…</strong>, <i>…</i>, <em>…</em>, <u>…</u>, "
                             "<ins>…</ins>, <s>…</s>, <strike>…</strike>, <del>…</del>")

        return extended_prompt
