import asyncio

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from handlers.logic import create_history, delete_history, search_history
from handlers.script import send_sorted_resumes

from .script import get_resume_data

router = Router()


class Form(StatesGroup):
    posada = State()
    misto = State()
    zarplata = State()
    dosvid = State()
    status = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [KeyboardButton(text="Допомога")],
        [KeyboardButton(text="Пошук кандидатів")],
        [KeyboardButton(text="Історія пошуку")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        "Привіт я створений аби допомогти тобі в пошуку кандидатів на потрібну тобі вакансію",
        reply_markup=keyboard,
    )


@router.message(lambda message: message.text == "Допомога")
async def process_with_puree(message: types.Message):
    text2 = """Розробка телеграм-ботів для вашого бізнесу під ключ @ds0903"""
    await asyncio.sleep(0.5)
    await message.answer(text2)
    await asyncio.sleep(1)
    await cmd_start(message)


@router.message(lambda message: message.text == "Пошук кандидатів")
async def cmd_poshuk(message: types.Message, state: FSMContext):
    await asyncio.sleep(0.5)
    kb = [
        [KeyboardButton(text="Work.ua")],
        [KeyboardButton(text="Robota.ua")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(
        "Виберіть на якому сайті шукати кандидатата", reply_markup=keyboard
    )


@router.message(lambda message: message.text == "Work.ua")
async def cmd_work(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardRemove()
    await message.answer(
        "Напишіть професію за якою шукаєте кандидата\nНаприклад : data-scientist",
        reply_markup=keyboard,
    )
    place = "Work.ua"
    await state.update_data(place=place)
    await state.set_state(Form.posada)


@router.message(lambda message: message.text == "Robota.ua")
async def cmd_robota(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardRemove()
    # await message.answer(
    #     "Напишіть посаду за якою шукаєте кандидата, наприклад : data-scientist",
    #     reply_markup=keyboard,
    # )
    # place = "Robota.ua"
    # await state.update_data(place=place)
    # await state.set_state(Form.posada)
    await asyncio.sleep(0.5)

    await message.answer(
        "Поки в розробці, виберіть краще work.ua",
        reply_markup=keyboard,
    )
    await asyncio.sleep(0.5)
    await cmd_poshuk(message, state)


@router.message(Form.posada)
async def process_posada(message: types.Message, state: FSMContext):
    posada = message.text
    await state.update_data(posada=posada)
    await state.set_state(Form.misto)
    await asyncio.sleep(0.5)
    await message.reply(
        f"Професія встановленна: {posada}\nТепер введіть назву міста кандидата"
    )


@router.message(Form.misto)
async def process_misto(message: types.Message, state: FSMContext):
    misto = message.text
    await state.update_data(misto=misto)
    await state.set_state(Form.zarplata)
    await asyncio.sleep(0.5)
    await message.reply(
        f"Місто встановленна: {misto}\nНапишіть через дефіс бажану зарплату\nНаприклад 1000-10000"
    )


@router.message(Form.zarplata)
async def process_zarplata(message: types.Message, state: FSMContext):
    zarplata = message.text.split("-")
    if len(zarplata) == 2:
        zarplata_ot, zarplata_do = zarplata
        await message.answer(
            f"Зарплата встановленна: от {zarplata_ot.strip()} до {zarplata_do.strip()}"
        )
    else:
        await message.answer(
            "Невірний формат введення. Введіть два значення через дефіс."
        )

    if (
        zarplata_ot >= zarplata_do
        or zarplata_do <= zarplata_ot
        or zarplata_ot == zarplata_do
    ):
        await asyncio.sleep(0.5)
        await message.answer(
            "Невірний формат введення. Зарплати повинні бути від меньшої до більшої."
        )
    else:

        await state.update_data(zarplata_ot=zarplata_ot)
        await state.update_data(zarplata_do=zarplata_do)

        await state.set_state(Form.dosvid)
        await asyncio.sleep(0.5)
        await message.reply("А також напишіть числом досвід в роках\nНаприклад 5")


@router.message(Form.dosvid)
async def process_dosvid(message: types.Message, state: FSMContext):
    dosvid = message.text
    try:
        dosvid == int(dosvid)
        await message.answer(f"Досвід встановленна: {dosvid}")
        await state.update_data(dosvid=dosvid)
    except ValueError:
        await message.answer("Невірний формат введення, спробуйте ще раз")

    user_id = message.from_user.id
    user_data = await state.get_data()
    posada = user_data.get("posada")
    misto = user_data.get("misto")
    zarplata_ot = user_data.get("zarplata_ot")
    zarplata_do = user_data.get("zarplata_do")
    dosvid = user_data.get("dosvid")

    place = user_data.get("place")
    await create_history(user_id, posada, misto, zarplata_ot, zarplata_do, dosvid)
    await state.clear()
    kb = [
        [KeyboardButton(text="Пошук кандидатів")],
        [KeyboardButton(text="Історія пошуку")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await asyncio.sleep(0.5)
    await message.reply(
        "Історію пошуку збережено",
        reply_markup=keyboard,
    )

    resumes = get_resume_data(posada, misto, zarplata_ot, zarplata_do, dosvid, place)
    if resumes == "Немає інформації":
        await asyncio.sleep(0.5)
        await message.answer(
            "Не знайдено кандедатів за вказаними критеріями, перевірьте правильність написання"
        )
    else:
        try:
            await send_sorted_resumes(resumes, message)
        except TypeError:
            await message.answer(
                "Не знайдено кандедатів за вказаними критеріями, перевірьте правильність написання"
            )


@router.message(lambda message: message.text == "Історія пошуку")
async def cmd_all(message: types.Message, state: FSMContext):
    user_data = await search_history(message.from_user.id)
    if user_data:
        for i in user_data:
            (
                id,
                user_id,
                posada,
                misto,
                zarplata_ot,
                zarplata_do,
                dosvid,
            ) = i
            await message.answer(
                f"Посада: {posada}\n"
                f"Місто: {misto}\n"
                f"Зарплата: від {zarplata_ot} до {zarplata_do}\n"
                f"Досвід: {dosvid}"
            )
            await asyncio.sleep(1)
        await message.answer("Очистити історію пошуку ? Так/Ні")
        await state.set_state(Form.status)
    else:
        await message.answer("Історія пошуку порожня")
        await asyncio.sleep(0.5)
        await cmd_start(message)


@router.message(Form.status)
async def process_dosvid(message: types.Message, state: FSMContext):
    if message.text == "Так":
        await delete_history(message.from_user.id)
        await state.clear()
        await asyncio.sleep(0.5)
        await message.answer("Історію пошуку очищено")
    elif message.text == "Ні":
        await state.clear()
        await asyncio.sleep(0.5)
        await cmd_start(message)
    else:
        await message.answer("Невірний формат введення, спробуйте ще раз Так/Ні")
