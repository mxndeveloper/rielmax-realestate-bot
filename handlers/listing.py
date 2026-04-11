from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_main_menu

router = Router()

class ListingForm(StatesGroup):
    waiting_for_photos = State()
    waiting_for_description = State()
    waiting_for_price = State()

@router.callback_query(F.data == "create_listing")
async def start_listing(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📸 Пришли фото квартиры (можно несколько)")
    await state.set_state(ListingForm.waiting_for_photos)
    await callback.answer()

@router.message(ListingForm.waiting_for_photos, F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def receive_photos(message: Message, state: FSMContext):
    # Extract photo file_ids
    if message.photo:
        file_ids = [photo.file_id for photo in message.photo]
    else:
        file_ids = [message.document.file_id]
    await state.update_data(photos=file_ids)
    await message.answer("✍️ Теперь напиши описание квартиры (район, метро, площадь, состояние)")
    await state.set_state(ListingForm.waiting_for_description)

@router.message(ListingForm.waiting_for_description, F.text)
async def receive_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Укажи цену в рублях (только цифры)")
    await state.set_state(ListingForm.waiting_for_price)

@router.message(ListingForm.waiting_for_price, F.text)
async def receive_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        data = await state.get_data()
        # Here you would save to database (listings table)
        await message.answer(
            f"✅ Объявление сохранено!\n💰 Цена: {price:,} ₽\n📝 Описание: {data['description'][:100]}...\n\n❤️ Riel скоро создаст продающий текст и виртуальный тур.",
            reply_markup=main_menu
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введи число (например: 15000000)")