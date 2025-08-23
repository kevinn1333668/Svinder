from pathlib import Path

from aiogram import F, Bot, Router
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext

from src.states import UserRoadmap, EditProfileStates
from src.keyboards.reply import main_menu_keyboard
from src.service.db_service import ServiceDB
from src.service.schemas import ProfileCreateInternalSchema
from src.static.text.texts import text_male, text_female


edit_router = Router()

UPLOAD_DIR_EDIT = Path('/app/src/static/users')
UPLOAD_DIR_EDIT.mkdir(parents=True, exist_ok=True)

TEXT_SKIP_BUTTON = "Оставить как есть ⏭️"

def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXT_SKIP_BUTTON)]], resize_keyboard=True, one_time_keyboard=True)

def sex_selection_horizontal_keyboard_with_skip() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_male), KeyboardButton(text=text_female)],
            [KeyboardButton(text=TEXT_SKIP_BUTTON)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


@edit_router.message(EditProfileStates.start)
async def edit_profile_start(message: Message, state: FSMContext, bot: Bot):
    current_profile = await ServiceDB.get_profile_by_tgid(message.from_user.id)
    if not current_profile:
        await message.answer("Сначала нужно создать анкету...", reply_markup=main_menu_keyboard())
        await state.clear()
        return
    await state.update_data(
        original_name=current_profile.name,
        original_age=current_profile.age,
        original_sex=current_profile.sex.value,
        original_uni=current_profile.uni,
        original_description=current_profile.description,
        original_s3_path=current_profile.s3_path
    )
    
    await message.answer(
        f"Начинаем редактирование. Текущее имя: {current_profile.name}. Введите новое или нажмите 'Оставить как есть'.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.name)


@edit_router.message(EditProfileStates.name)
async def edit_profile_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(name=data["original_name"])
    elif not message.text:
        await message.answer("Это не похоже на имя. Попробуй еще раз или оставь как есть.", reply_markup=skip_keyboard())
        return
    elif len(message.text) < 2 or len(message.text) > 64:
        await message.answer("Слишком длинное или короткое имя! Давай по новой или оставь как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(name=message.text)

    updated_data = await state.get_data()
    await message.answer(
        f"Имя обновлено на: {updated_data['name']}. Текущий возраст: {data['original_age']}. Введите новый или оставьте как есть.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.age)


@edit_router.message(EditProfileStates.age)
async def edit_profile_age(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(age=data["original_age"])
    elif not message.text or not message.text.isdigit():
        await message.answer("Это точно число? Попробуй еще раз или оставь как есть.", reply_markup=skip_keyboard())
        return
    elif int(message.text) < 16 or int(message.text) > 60:
        await message.answer("Странный возраст... Подумай еще или оставь как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(age=int(message.text))
    
    updated_data = await state.get_data()
    await message.answer(
        f"Возраст обновлен на: {updated_data['age']}. Текущий пол: {data['original_sex']}. Выберите новый или оставьте как есть.",
        reply_markup=sex_selection_horizontal_keyboard_with_skip()
    )
    await state.set_state(EditProfileStates.sex)


@edit_router.message(EditProfileStates.sex)
async def edit_profile_sex(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(sex=data["original_sex"])
    elif message.text not in [text_female, text_male]:
        await message.answer("Выберите пол из предложенных или оставьте как есть.", reply_markup=sex_selection_horizontal_keyboard_with_skip())
        return
    else:
        await state.update_data(sex='Девочка' if message.text == text_female else 'Мальчик')

    updated_data = await state.get_data()
    await message.answer(
        f"Пол обновлен на: {updated_data['sex']}. Текущий город: {data['original_uni']}. Введите новый или оставьте как есть.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.university)


@edit_router.message(EditProfileStates.university)
async def edit_profile_city(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(uni=data["original_uni"])
    else:
        await state.update_data(uni=message.text.upper())

    updated_data = await state.get_data()
    await message.answer(
        f"Город обновлен на: {updated_data['uni']}. Текущее описание: \"{data['original_description']}\". Напишите новое или оставьте как есть.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.description)


@edit_router.message(EditProfileStates.description)
async def edit_profile_description(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(description=data["original_description"])
    elif not message.text:
        await message.answer("Пустое описание? Попробуйте еще раз или оставьте как есть.", reply_markup=skip_keyboard())
        return
    elif len(message.text) > 1024:
        await message.answer("Слишком длинное описание! Максимум 1024 символа. Попробуйте еще раз или оставьте как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(description=message.text)
    
    updated_data = await state.get_data()
    await message.answer(
        f"Описание обновлено. Текущее фото: (отправлю его следующим сообщением, если есть).\nОтправьте новое фото или нажмите 'Оставить как есть'.",
        reply_markup=skip_keyboard()
    )
    if data.get("original_s3_path"):
        try:
            original_photo = data["original_s3_path"]
            await message.answer_photo(photo=original_photo, caption="Текущее фото.")
        except Exception as e:
            print(f"Error sending original photo: {e}")
            await message.answer("Не удалось загрузить текущее фото.")

    await state.set_state(EditProfileStates.photo)


@edit_router.message(EditProfileStates.photo)
async def edit_profile_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    final_s3_path = data["original_s3_path"]

    if message.text == TEXT_SKIP_BUTTON:
        file_id=final_s3_path
    elif not message.photo:
        await message.answer("Это не фото. Отправьте фото или оставьте старое.", reply_markup=skip_keyboard())
        return
    else:
        file_id = message.photo[-1].file_id
        

    await state.update_data(s3_path=file_id)
    
    updated_data = await state.get_data()

    profile_update_schema = ProfileCreateInternalSchema(
        tg_id=message.from_user.id,
        name=updated_data["name"],
        age=updated_data["age"],
        sex=updated_data["sex"],
        uni=updated_data["uni"],
        description=updated_data["description"],
        s3_path=updated_data["s3_path"],
    )

    try:
        await ServiceDB.update_profile(profile_update_schema)
    except Exception as e:
        print(f"ERROR during profile photo edit: {e}")
        await message.answer(f"Хмм, странно... Что-то нехорошее произошло...", reply_markup=main_menu_keyboard())
        await state.set_state(UserRoadmap.main_menu)
        return

    caption_text = (
        f"Анкета обновлена!\n"
        f"Имя: {profile_update_schema.name}\n"
        f"Возраст: {profile_update_schema.age}\n"
        f"Пол: {profile_update_schema.sex.value}\n"
        f"Город: {profile_update_schema.uni}\n"
        f"Описание: {profile_update_schema.description}"
    )

    if updated_data["s3_path"]:
        try:
            final_profile_image = updated_data["s3_path"]
            await message.answer_photo(
                photo=final_profile_image,
                caption=caption_text,
                reply_markup=main_menu_keyboard(),
                parse_mode="Markdown",
            )
        except Exception as e:
            print(f"Error sending final photo: {e}")
            await message.answer(caption_text + "\n\n(Не удалось загрузить фото для показа)", reply_markup=main_menu_keyboard())
    else:
        await message.answer(caption_text + "\n\n(Фото не установлено)", reply_markup=main_menu_keyboard())


    await state.clear()
    await state.set_state(UserRoadmap.main_menu)
