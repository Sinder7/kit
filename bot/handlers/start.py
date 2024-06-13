from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database.db import User
from states import RegisterState


router = Router()


@router.message(CommandStart())
async def cmd_start(is_teacher: types.Message, state: FSMContext):
    if User.if_user_exists(message.from_user.id):
        kb = [
            [types.KeyboardButton(text="Расписание на сегодня")],
            [types.KeyboardButton(text="Расписание на завтра")],
            [types.KeyboardButton(text="Расписание на неделю")],
        ]

        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Добро пожаловать!", reply_markup=keyboard)
    else:
        status_kb = [
            [types.KeyboardButton(text="Студент")],
            [types.KeyboardButton(text="Преподаватель")],
        ]
        status_keyboard = types.ReplyKeyboardMarkup(
            keyboard=status_kb, resize_keyboard=True
        )
        await message.answer(
            "Салам Алейкум\nДобро пожаловать!\n" "Выберите ваш статус:",
            reply_markup=status_keyboard,
        )

        await state.set_state(RegisterState.status)


@dp.message(StateFilter(RegisterState.status))
async def get_status(message: types.Message, state: FSMContext):
    """ """
    if message.text != "Студент" and message.text != "Преподаватель":
        await message.answer("Упс, произошла ошибка\nПопробуйте еще раз")
        return

    await state.update_data(status=message.text)

    if message.text == "Студент":
        await state.set_state(RegisterState.group)
        await message.answer(
            "Введите название группы\nК примеру: ИС-22",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    if message.text == "Преподаватель":
        await state.set_state(RegisterState.group)
        await message.answer(
            "Введите ФИО как в расписании\nК примеру: Иванов И.А", reply_markup=None
        )


@dp.message(StateFilter(RegisterState.status))
async def get_status(message: types.Message, state: FSMContext):
    """ """
    if message.text != "Студент" and message.text != "Преподаватель":
        await message.answer("Упс, произошла ошибка\nПопробуйте еще раз")
        return

    await state.update_data(status=message.text)

    if message.text == "Студент":
        await state.set_state(RegisterState.group)
        await message.answer(
            "Введите название группы\nК примеру: ИС-22",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    if message.text == "Преподаватель":
        await state.set_state(RegisterState.group)
        await message.answer(
            "Введите ФИО как в расписании\nК примеру: Иванов И.А", reply_markup=None
        )


@router.message(StateFilter(RegisterState.group))
async def get_group(message: types.Message, state: FSMContext):
    """
    :param message: The message object received from the user.
    :param state: The FSMContext object for managing the state of the user.
    :return: None

    This method is used to handle the user's input for selecting a group during the registration process.
    If the user's status is 'Преподаватель', it sends a new registration request to the admin with the user's
    information.
    If the user's status is not 'Преподаватель', it registers the user with the selected group and sends a success
    message to the user.

    Example usage:
    ```python
    await get_group(message, state)
    ```
    """
    await state.update_data(group=message.text)
    state_data = await state.get_data()

    if state_data["status"] == "Преподаватель":

        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text="Подтвердить ✅", callback_data=f"accept:{message.from_user.id}"
            )
        )
        builder.row(
            types.InlineKeyboardButton(
                text="Отклонить ❌", callback_data=f"decline:{message.from_user.id}"
            )
        )
        keyboard = builder.as_markup()

        await bot.send_message(
            chat_id=config.admin_chat,
            text=f"Новая заявка на регистрацию:\n"
            f"Username: {message.from_user.full_name}\n"
            f"ID: {message.from_user.id}\n"
            f"Имя: {message.text}\n"
            f"Ссылка на профиль: https://t.me/{message.from_user.username}",
            reply_markup=keyboard,
        )

        user = User(
            id=message.from_user.id,
            name=message.text,
            username=message.from_user.username,
            status="wait",
        )

        await message.answer(
            "Заявка на регистрацию отправлена администратору\nОжидайте подтверждения"
        )

    else:
        if message.text.lower() not in config.groups:
            await message.answer("Такой группы не существует\nПопробуйте еще раз")
            return

        user = User(
            id=message.from_user.id,
            name=message.from_user.full_name,
            username=message.from_user.username,
            status=state_data["status"],
            group=message.text.lower(),
        )
        await message.answer("Вы успешно зарегистрированы\nВведите /start")

    user.add()
    await state.clear()
