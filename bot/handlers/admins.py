import os

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db import User
from states import SpamState
from utils import restart_bot
from filters import is_admin


router = Router()
router.message.filter(is_admin)


@router.message(F.document)
async def handle_document(message: types.Message):

    if message.document.mime_type != "application/json":
        await message.answer("Файл должен быть JSON.")
        return

    os.remove(timetable_file)

    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, timetable_file)

    restart_bot()

    await message.answer("Расписание успешно обновлено.")


@router.message(Command("spam"))
async def cmd_spam(message: types.Message, state: FSMContext):
    """ """
    args = message.text.split(" ")
    print(args)
    if len(args) <= 1:
        await message.answer("Команда введена неверно!\nПример: /spam ИС-12")
        return
    await state.set_state(SpamState.group)
    await state.update_data(group=args[1])
    await state.set_state(SpamState.text)
    await message.answer(
        "Введите текст рассылки\n\n"
        "К примеру:\n"
        "Замена - ИС12, 3я пара\n"
        "Предмет - Математика\n"
        "Аудитория - 123\n"
    )


@router.message(StateFilter(SpamState.text))
async def get_text(message: types.Message, state: FSMContext):
    """ """
    await state.update_data(text=message.text)
    await message.answer("Рассылка началась!")
    count = 0
    state_data = await state.get_data()
    if state_data["group"] == "all":
        users = User.get_all()
    else:
        users = User.get_all_group(state_data["group"])

    for user in users:
        try:
            await bot.send_message(user.id, message.text)
            await asyncio.sleep(0.5)
            count += 1
        except:
            pass
    await message.answer(
        "Рассылка завершена!\nПолучили сообщение: " + str(count) + " человек"
    )
    await state.clear()
