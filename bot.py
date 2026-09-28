import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Bularni o'zingizniki bilan almashtiring:
BOT_TOKEN = "8837550445:AAHf07Q7EooDoyObC8reK8A_F2GkBaFV2Nw"
GAME_SHORT_NAME = "math_battle_reverse" # Masalan: math_battle_reverse
GAME_URL = "math-battle-reverse-2z1fqmcws-lynx-fb43.vercel.app/index.html" # 3-bosqichda ushbu havolani olasiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_game_cmd(message: types.Message):
    await bot.send_game(
        chat_id=message.chat.id,
        game_short_name=GAME_SHORT_NAME
    )

@dp.callback_query(lambda c: c.game_short_name is not None)
async def process_game_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(
        callback_query_id=callback_query.id,
        url=GAME_URL
    )

async def main():
    # Eski Webhook'ni va fonda qolib ketgan so'rovlarni o'chiramiz
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Botni ishga tushiramiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())