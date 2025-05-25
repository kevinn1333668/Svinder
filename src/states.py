from aiogram.fsm.state import State, StatesGroup


class StartStates(StatesGroup):
    start = State()
    get_token = State()
    main_menu = State()
