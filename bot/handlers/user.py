import os
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db import User
from utils import restart_bot, get_day_teacher_time, day_number, get_day_data_text


router = Router()


@router.message(F.text == "Расписание на сегодня")
async def get_today(message: types.Message):
    """ """
    day_number = datetime.today().weekday() + 1
    if User.get_user(message.from_user.id).status == "преподаватель":
        await message.answer(
            get_day_teacher_time(
                teacher_name=User.get_user(message.from_user.id).name,
                day_number=day_number,
            )
        )
        print(User.get_user(message.from_user.id).name)
    else:
        await message.answer(
            get_day_data_text(day_number, User.get_user(message.from_user.id).group)
        )


@router.message(F.text == "Расписание на завтра")
async def get_tomorrow(message: types.Message):
    """ """
    day_number = datetime.today().weekday() + 2
    if day_number == 7 or day_number == 8:
        await message.answer("Завтра выходной")
        return
    if "преподаватель" == User.get_user(message.from_user.id).status:
        await message.answer(
            get_day_teacher_time(
                teacher_name=User.get_user(message.from_user.id).name,
                day_number=day_number,
            )
        )
    else:
        await message.answer(
            get_day_data_text(day_number, User.get_user(message.from_user.id).group)
        )


@router.message(F.text == "Расписание на неделю")
async def get_week(message: types.Message):
    """ """
    if User.get_user(message.from_user.id).status == "преподаватель":
        for i in range(1, 7):
            messages = get_day_teacher_time(
                teacher_name=User.get_user(message.from_user.id).name, day_number=i
            )
            await message.answer(messages)

    else:
        user_group = User.get_user(message.from_user.id).group
        for i in range(1, 7):
            await message.answer(get_day_data_text(i, user_group))


@router.message(Command("notify"))
async def cmd_notify(message: types.Message):
    """
    :param message: Telegram message object
    :return: None
    """
    user = User.get_user(message.from_user.id)
    user.reverse_notify()
    user.update()
    if user.notify:
        await message.answer(
            "Уведомления включены\n Вы будете получать расписание на завтра каждый день в 19:30"
        )
    else:
        await message.answer("Уведомления выключены")


@router.message(Command("change_group"))
async def cmd_change_group(message: types.Message, state: FSMContext):
    """
    :param message: The message object that triggered the command.
    :param state: The FSMContext object to manage the state of the conversation.
    :return: None.
    """
    if User.get_user(message.from_user.id).status == "преподаватель":
        await message.answer("Команда доступна только студентам")
        return
    await message.answer("Введите новое название группы\nК примеру: ИС-12")
    await state.set_state(ChangeGroupState.group)


@router.message(Command("change_name"))
async def cmd_change_name(message: types.Message, state: FSMContext):
    """ """
    if User.get_user(message.from_user.id).status == "студент":
        await message.answer("Команда доступна только преподавателям")
        return
    await message.answer("Введите новое ФИО как в расписании\nК примеру: Иванов И.А")
    await state.set_state(ChangeGroupState.group)


@router.message(Command("delete_me"))
async def cmd_delete_me(message: types.Message):
    """ """
    user = User.get_user(message.from_user.id)
    user.delete()
    await message.answer(
        "Информация о вас была удалена из базы данных бота\nВведите /start"
    )


@router.message(StateFilter(ChangeGroupState.group))
async def change_group(message: types.Message, state: FSMContext):
    """
    :param message: The message from the user
    :param state: The FSMContext object for storing the state of the conversation
    :return: None

    This method is used to change the group of a user in the database. It takes the user's message and the FSMContext
    object as parameters.

    If the user is a teacher, it updates the user's name to the new group and sends a success message to the user.

    If the user is a student, it updates the user's group to the new group and sends a success message to the user.

    If there is an error, it sends an error message to the user and returns.

    Finally, it updates the user's information in the database and clears the state.
    """

    user = User.get_user(message.from_user.id)
    new_group = message.text.lower()
    if new_group not in config.groups:
        await message.answer("Такой группы не существует\nПопробуйте еще раз")
        return
    if user.status == "преподаватель":
        user.name = new_group.lower()
        await message.answer("Ваше ФИО успешно изменено на " + new_group)
    elif user.status == "студент":
        user.group = new_group.lower()
        await message.answer("Ваша группа успешно изменена на " + new_group)
    else:
        await message.answer("Упс, произошла ошибка\nПопробуйте еще раз")
        return

    user.update()
    await state.clear()
