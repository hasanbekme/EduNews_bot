from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext
from db.models import User, MediaCategory, Media
from filters.common import TranslatedText
from filters.states import DigitalEducationState
from keyboards.reply_markup import media_category_tm, media_list_tm
from localization.strings import _
from middlewares.base_middlewares import PermissionMiddleware
from utils.shortcuts import send_main_menu

router = Router()
router.message.middleware(PermissionMiddleware())


@router.message(TranslatedText("digital_education"))
async def menu_digital_education(message: types.Message, user: User, state: FSMContext):
    data = await media_category_tm(user=user)
    if data is None:
        return
    await message.answer(**data)
    await state.set_state(DigitalEducationState.category_list)


@router.message(DigitalEducationState(), TranslatedText("back"))
async def back_button(message: types.Message, user: User, state: FSMContext):
    current_state = await state.get_state()
    if current_state == DigitalEducationState.category_list:
        await send_main_menu(message=message, user=user)
    elif current_state == DigitalEducationState.media_list:
        data = await media_category_tm(user=user)
        if data is None:
            return
        await message.answer(**data)
        await state.set_state(DigitalEducationState.category_list)


@router.message(DigitalEducationState.category_list, F.content_type == "text")
async def select_category(message: types.Message, user: User, state: FSMContext):
    category = await MediaCategory.get_or_none(name=message.text[2:])
    if category is None:
        return
    await state.update_data(category=category.pk)
    data = await media_list_tm(user=user, category=category)
    await message.answer(**data)
    await state.set_state(DigitalEducationState.media_list)


@router.message(DigitalEducationState.media_list, F.content_type == "text")
async def retrieve_media(message: types.Message, user: User, state: FSMContext):
    state_data = await state.get_data()
    media = await Media.get_or_none(
        title=message.text[2:], category__id=state_data["category"]
    )
    if media is None:
        return
    await message.answer(text=f"<a href='{media.url}'>📹 {media.title}</a>")