from aiogram.fsm.state import StatesGroup, State


class RegisterState(StatesGroup):
    """
    Represents the state of the registration process.

    Attributes:
        status (State): Represents the status of the registration process.
        group (State): Represents the group of the registration process.
    """

    status = State()
    group = State()


class SpamState(StatesGroup):
    """
    Represents the state of a spam.

    States:
        - group: Represents the group state.
        - text: Represents the text state.
    """

    group = State()
    text = State()


class ChangeGroupState(StatesGroup):
    """
    Represents the states for changing a group.

    :ivar group: The state representing the group.
    :vartype group: :class:`aiogram.fsm.state.State`
    """

    group = State()
