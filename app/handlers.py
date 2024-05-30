from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.types import CallbackQuery
from aiogram.filters import CommandStart, Command
import app.database.requests as rq

import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.save_user(message.from_user.id)
    await message.answer("Hello!\n"
                         'How can I help?\n'
                         '(To understand my functions call: /help)')


@router.message(Command('help'))
async def cmd_start(message: Message):
    await message.answer("Hello!\n"
                         "You can see all my commands here.\n"
                         "/start - starting to work with me.\n"
                         "/help - You are here\n"
                         "/my_photos - I'll give you all your photos.\n"
                         "You can click the delete button under the photo and I'll delete it.\n"
                         "Send me photos, and I save them.")


@router.message(F.photo)
async def accept_photos(message: Message, bot, album: list = None):
    for obj in album:
        file_id = obj.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        file = await bot.download_file(file_info.file_path)
        photo_bytes = file.read()
        if not await rq.user_photo_in_base(photo_bytes=photo_bytes, user_id=message.from_user.id):
            await rq.save_photo(photo_bytes, message.from_user.id, file_id)

    await message.answer("Photos have been saved to the database.")


@router.message(Command('my_photos'))
async def show_photos(message: Message, bot):
    user_id = message.from_user.id
    photos = await rq.get_user_photos(user_id)
    if not photos:
        await message.reply("You don't have any saved photos.")
        return

    for idx, photo in enumerate(photos):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="delete", callback_data=f"delete_{idx}")]
        ])

        photo_file = BufferedInputFile(BytesIO(photo.photo_data).getvalue(), filename=f"photo_{idx}.jpg")

        await bot.send_photo(user_id, photo=photo_file, caption=f"Photo {idx + 1}", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith('delete_'))
async def delete_photo_callback(callback_query: CallbackQuery, bot):
    user_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[1])
    photos = await rq.get_user_photos(user_id)

    if 0 <= idx < len(photos):
        photo_bytes = photos[idx].photo_data
        await rq.delete_photo_by_bytes(user_id, photo_bytes)
        await callback_query.answer("Photo deleted")
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    else:
        await callback_query.answer("ERROR")
