import asyncio
import io
import re
from aiogram import Router, types, Bot
from functools import wraps
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramUnauthorizedError, TelegramNetworkError
import time
import smtplib
import imaplib
from aiohttp import ClientConnectorError
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError

from .errors import *
from bot_instance import logger, client, bot


# _MD_V2_SPECIAL = r'.!()-+'
# _ESCAPE_PATTERN = re.compile(r'([{}])'.format(re.escape(_MD_V2_SPECIAL)))


def escape_md_v2(text: str) -> str:
    return text
    # return _ESCAPE_PATTERN.sub(r'\\\1', text)


def db_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Error404 as e:
            logger.exception(str(e))
            return None
        except DatabaseConnectionError as e:
            logger.exception(str(e))
            return None
        except Error409 as e:
            logger.exception(str(e))
            return None
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None
    return wrapper


def gpt_error_handler(func):
    @wraps(func)
    async def wrapper(*args, retry_attempts=3, delay_between_retries=5, **kwargs):
        for attempt in range(retry_attempts):
            try:
                return await func(*args, **kwargs)
            except ParseError as e:
                logger.exception(f"{str(e)}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"{str(e)}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except ContentError as e:
                logger.exception(f"{str(e)}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"{str(e)}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except AuthenticationError as e:
                logger.exception(f"Authentication Error: {e}")
                return None
            except RateLimitError as e:
                logger.exception(f"Rate Limit Exceeded: {e}")
                return None
            except APIConnectionError as e:
                logger.exception(f"API Connection Error: {e}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"API Connection Error: {e}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except APIError as e:
                logger.exception(f"API Error: {e}")
                return None
            except Exception as e:
                logger.exception(f"Неизвестная ошибка: {str(e)}")
                return None
    return wrapper


router = Router()


@router.errors()
async def global_error_handler(update: types.Update, exception: Exception):
    if isinstance(exception, TelegramBadRequest):
        logger.error(f"Некорректный запрос: {exception}. Пользователь: {update.message.from_user.id}")
        return True
    elif isinstance(exception, TelegramRetryAfter):
        logger.error(f"Request limit exceeded. Retry after {exception.retry_after} seconds.")
        await asyncio.sleep(exception.retry_after)
        return True
    elif isinstance(exception, TelegramUnauthorizedError):
        logger.error(f"Authorization error: {exception}")
        return True
    elif isinstance(exception, TelegramNetworkError):
        logger.error(f"Network error: {exception}")
        await asyncio.sleep(5)
        return True
    else:
        logger.exception(f"Неизвестная ошибка: {exception}")
        return True


async def safe_send_message(bott: Bot, recipient, text: str, reply_markup=ReplyKeyboardRemove(), retry_attempts=3, delay=5) -> Message:
    """Отправка сообщения с обработкой ClientConnectorError, поддержкой reply_markup и выбором метода отправки."""

    for attempt in range(retry_attempts):
        try:
            if isinstance(recipient, types.Message):
                msg = await recipient.answer(escape_md_v2(text), reply_markup=reply_markup,
                                             parse_mode=ParseMode.HTML)
            elif isinstance(recipient, types.CallbackQuery):
                msg = await recipient.message.answer(escape_md_v2(text), reply_markup=reply_markup,
                                                     parse_mode=ParseMode.HTML)
            elif isinstance(recipient, int):
                msg = await bott.send_message(chat_id=recipient, text=escape_md_v2(text), reply_markup=reply_markup,
                                              parse_mode=ParseMode.HTML)
            else:
                raise TypeError(f"Неподдерживаемый тип recipient: {type(recipient)}")

            return msg

        except ClientConnectorError as e:
            logger.error(f"Ошибка подключения: {e}. Попытка {attempt + 1} из {retry_attempts}.")
            if attempt < retry_attempts - 1:
                await asyncio.sleep(delay)
            else:
                logger.error(f"Не удалось отправить сообщение после {retry_attempts} попыток.")
                return None
        except Exception as e:
            logger.error(str(e))
            return None


@gpt_error_handler
async def create_thread():
    thread = client.beta.threads.create()
    return thread.id


@gpt_error_handler
async def transcribe(message: Message) -> str:
    voice_file = io.BytesIO()
    voice_file_id = message.voice.file_id
    file = await bot.get_file(voice_file_id)
    await bot.download_file(file.file_path, voice_file)
    voice_file.seek(0)
    voice_file.name = "voice_message.ogg"

    return client.audio.transcriptions.create(
        model="whisper-1",
        file=voice_file,
        response_format="text"
    )


@gpt_error_handler
async def gpt_assistant_mes(thread_id, assistant_id, mes) -> str:
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=mes
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    data = messages.data[0].content[0].text.value.strip()

    if not data:
        raise ContentError
    return data
