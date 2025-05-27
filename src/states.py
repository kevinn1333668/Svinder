from aiogram.fsm.state import State, StatesGroup


class UserRoadmap(StatesGroup):
    start = State()
    get_token = State()
    check_token = State()
    main_menu = State()
