import io

from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.payload import decode_payload, encode_payload
from aiogram.exceptions import TelegramBadRequest


from errors.handlers import safe_send_message, create_thread, transcribe, gpt_assistant_mes
from keyboards.keyboards import fb_ikb, get_new_vacancy_kb
from bot_instance import bot, client
from database.req import *

router = Router()


welcome_msg = """
Привет! 
Я бот, который поможет описать новую позицию в компании.

Со мной можно общаться текстом и голосовыми сообщениями. 

Чтобы начать напиши - /vacancy или просто новая вакансия.
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    if not await get_user(message.from_user.id):
        await create_user(message.from_user.id)
    await safe_send_message(bot, message, welcome_msg, get_new_vacancy_kb())


class CreateResume(StatesGroup):
    create_loop = State()
    waiting_fb = State()


@router.message(F.text.lower().contains("новая вакансия"))
async def create_resume05(callback: CallbackQuery, state: FSMContext):
    thread = await create_thread()
    prompt = await create_extended_prompt()
    msg: str = await gpt_assistant_mes(thread, 'asst_NtVWkelDriet0dw9fSf8WYdr', prompt)
    await state.set_data({'thread': thread})
    await safe_send_message(bot, callback, msg)
    await state.set_state(CreateResume.create_loop)


@router.message(Command('vacancy'))
async def create_resume(message: Message, state: FSMContext):
    thread = await create_thread()
    prompt = await create_extended_prompt()
    msg: str = await gpt_assistant_mes(thread, 'asst_NtVWkelDriet0dw9fSf8WYdr', prompt)
    await state.set_data({'thread': thread})
    await safe_send_message(bot, message, msg)
    await state.set_state(CreateResume.create_loop)


@router.message(CreateResume.create_loop)
async def gpt_conv(message: Message, state: FSMContext):
    data = await state.get_data()
    thread = data.get('thread', 0)

    if message.voice:
        text = await transcribe(message)
    else:
        text = message.text

    msg: str = await gpt_assistant_mes(
        thread_id=thread,
        assistant_id='asst_NtVWkelDriet0dw9fSf8WYdr',
        mes=text
    )

    res_pattern = msg.startswith('&')
    if res_pattern != -1:
        # try:
        await safe_send_message(bot, message, text=msg[1:], reply_markup=fb_ikb())
        # except TelegramBadRequest as e:
        #     msg: str = await gpt_assistant_mes(thread_id=thread, assistant_id='asst_NtVWkelDriet0dw9fSf8WYdr',
        #                                        mes="Напиши еще раз, но не используй никакие символы или теги, "
        #                                            "которые не поддерживает telegram")
        #     await safe_send_message(bot, message, text=msg[1:], reply_markup=fb_ikb())
        await state.update_data({'plain': msg[1:]})
        await state.set_state(CreateResume.waiting_fb)
    else:
        # try:
        await safe_send_message(bot, message, text=msg)
        # except TelegramBadRequest as e:
        #     msg: str = await gpt_assistant_mes(thread_id=thread, assistant_id='asst_NtVWkelDriet0dw9fSf8WYdr',
        #                                        mes="Напиши еще раз, но не используй никакие символы или теги, "
        #                                            "которые не поддерживает telegram")
        #     await safe_send_message(bot, message, text=msg, reply_markup=get_end_ikb())


@router.callback_query(StateFilter(CreateResume.waiting_fb), F.data == 'fb_yes')
async def good_end(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plain = data.get('plain', '')
    await add_reference(plain)
    await safe_send_message(bot, callback, text="Спасибо, это будет учтено", reply_markup=get_new_vacancy_kb())
    await callback.answer()
    await state.clear()


@router.callback_query(StateFilter(CreateResume.waiting_fb), F.data == 'fb_no')
async def bad_end(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Спасибо, это будет учтено", reply_markup=get_new_vacancy_kb())
    await callback.answer()
    await state.clear()
