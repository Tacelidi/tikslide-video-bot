import asyncio
import re
from aiogram import F
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from videomaker import create_video
from concurrent.futures import ThreadPoolExecutor
from aiogram.types import FSInputFile
import shutil
from dotenv import load_dotenv
import os

executor = ThreadPoolExecutor(max_workers=2)

async def run_blocking(func,*args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor,func,*args)

logging.basicConfig(level=logging.INFO)

class UserState(StatesGroup):
    getting_link = State()

load_dotenv()
bot = Bot(
    token=os.getenv('TOKEN'),
    default = DefaultBotProperties(
        parse_mode = ParseMode.HTML
    )
)

dp = Dispatcher()

markup = types.ReplyKeyboardRemove()

@dp.message(F.text, Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    buttons =[
        [
            types.KeyboardButton(text = "Send a link")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu"
    )
    await message.answer(f"{html.bold(html.quote('Hello, ' + message.from_user.first_name))}. This bot can make a video from a TikTok \'SlideShow\'. Just send a link and get your video!",reply_markup=keyboard)

@dp.message(F.text == "Send a link")
async def cmd_send_link(message: types.Message, state: FSMContext):
    await message.answer("Waiting for your link",reply_markup=markup)
    await state.set_state(UserState.getting_link)

@dp.message(UserState.getting_link)
async def cmd_get_link(message: types.Message, state: FSMContext):
    buttons =[
        [
            types.KeyboardButton(text = "Send a link")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu"
    )
    link = message.text
    pattern = r'https://vt.tiktok.com/'
    if len(re.findall(pattern,link)) != 0:
        status_msg = await message.answer("Started production...")
        try:
            id = message.from_user.id
            await run_blocking(create_video,link,id)
            await status_msg.delete()
            video = FSInputFile("content882150010/output.mp4")
            await message.answer_video(video)
            await status_msg.delete()
            await message.answer("Done!",reply_markup=keyboard)
            shutil.rmtree(f"content{id}")
            await state.clear()
        except Exception as e:
            await status_msg.delete()
            await message.answer("Something went wrong. Try again later.",reply_markup=keyboard)
    else:
        await message.answer("This links seems not correct.Try again.",reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

