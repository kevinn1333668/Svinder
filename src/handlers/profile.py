from pathlib import Path

from aiogram import F, Bot
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext

from src.states import UserRoadmap, CreateProfileStates
from src.keyboards.reply import sex_selection_horizontal_keyboard, main_menu_keyboard
from src.service.db_service import ServiceDB
from src.service.schemas import ProfileCreateInternalSchema
from src.static.text.texts import text_male, text_female


profile_router = Router()

UPLOAD_DIR = Path('/app/src/static/users')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@profile_router.message(CreateProfileStates.start)
async def profile_start(message: Message, state: FSMContext):
    await message.answer(
        "Введи свое имя",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CreateProfileStates.name)


@profile_router.message(CreateProfileStates.name)
async def profile_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Боюсь ты где-то ошибся, попробуй еще раз",
            reply_markup=ReplyKeyboardRemove()
        )
    elif len(message.text) < 2 or len(message.text) > 64:
        await message.answer(
            "Слишком длинное или короткое имя! Давай по новой..",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(name=message.text)
        await message.answer(
            f"Отлично, {message.text}, теперь твой возраст",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(CreateProfileStates.age)


@profile_router.message(CreateProfileStates.age)
async def profile_age(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Боюсь ты где-то ошибся, попробуй еще раз",
            reply_markup=ReplyKeyboardRemove()
        )
    elif not message.text.isdigit():
        await message.answer(
            "Странный возраст... Это точно число, не могу понять? Давай еще раз",
            reply_markup=ReplyKeyboardRemove()
        )
    elif int(message.text) < 16 or int(message.text) > 60:
        await message.answer(
            "Странный возраст... Подумай еще",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(age=int(message.text))
        await message.answer(
            f"Отлично, тебе {message.text} лет, фиксирую. Теперь укажи, ты парень или девушка?",
            reply_markup=sex_selection_horizontal_keyboard()
        )
        await state.set_state(CreateProfileStates.sex)


@profile_router.message(CreateProfileStates.sex)
async def profile_sex(message: Message, state: FSMContext):
    if message.text != text_female and message.text != text_male:
        await message.answer(
            "Боюсь ты где-то ошибся, попробуй еще раз",
            reply_markup=sex_selection_horizontal_keyboard()
        )
    else:
        if message.text == text_female:
            await state.update_data(sex='female')
        else:
            await state.update_data(sex='male')
        await message.answer(
            "Записал. Теперь скажи свой университет",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CreateProfileStates.university)


@profile_router.message(CreateProfileStates.university)
async def profile_university(message: Message, state: FSMContext):
    if message.text.upper() not in ["БГУ", "БГУИР", "БНТУ", "БГТУ", "БГМУ", "МГЛУ", "БГЭУ", "СКОРИНА", "СКАРЫНА", "СКОРЫНА", "ГГМУ"]:
        await message.answer(
            "Это разве уник? Давай по-нормальному",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(uni=message.text.upper())
        await message.answer(
            "Напиши о себе: хобби, интересы и увлечения",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CreateProfileStates.description)


@profile_router.message(CreateProfileStates.description)
async def profile_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        f"Последний этап! Отправь фото для своей анкеты.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CreateProfileStates.photo)


@profile_router.message(CreateProfileStates.photo)
async def profile_photo(message: Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer(
            f"Вряд ли это фотка! Попробуй еще раз",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        photo_size = message.photo[-1]
        dest_path = UPLOAD_DIR / (str(message.from_user.id) + ".jpg")
        
        await bot.download(
            photo_size,
            destination=dest_path
        )
        data = await state.get_data()
        profile = ProfileCreateInternalSchema(
            tg_id=message.from_user.id,
            name=data["name"],
            age=data["age"],
            sex=data["sex"],
            uni=data["uni"],
            description=data["description"],
            s3_path=str(dest_path),
        )

        await ServiceDB.add_profile(profile)

        profile_image = FSInputFile(str(dest_path))

        await message.answer_photo(
            photo=profile_image,
            caption="Анкета сделана",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )

        await state.set_state(UserRoadmap.main_menu)
