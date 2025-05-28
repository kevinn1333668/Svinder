from aiogram.fsm.state import State, StatesGroup


class UserRoadmap(StatesGroup):
    start = State()
    get_token = State()
    check_token = State()
    main_menu = State()


class CreateProfileStates(StatesGroup):
    start = State()
    name = State()
    age = State()
    sex = State()
    university = State()
    description = State()
    photo = State()


class SearchProfileStates(StatesGroup):
    get_profile = State()
    like = State()
    dislike = State()

