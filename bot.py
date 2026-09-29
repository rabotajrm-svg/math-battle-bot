import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8837550445:AAHf07Q7EooDoyObC8reK8A_F2GkBaFV2Nw")
GAME_URL = os.getenv("GAME_URL", "math-battle-reverse-2z1fqmcws-lynx-fb43.vercel.app/index.html")
GAME_SHORT_NAME = "math_battle_reverse"  # BotFather'dagi o'yin nomi

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# 1. Start va O'yin xabarini yuborish
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await bot.send_game(
        chat_id=message.chat.id,
        game_short_name=GAME_SHORT_NAME
    )


# 2. O'ynash tugmasi bosilganda WebApp ochish
@dp.callback_query(F.game_short_name)
async def game_callback_handler(callback: types.CallbackQuery):
    user = callback.from_user
    name = f"@{user.username}" if user.username else user.first_name
    # URL ga ism va ID ni biriktirib yuboramiz
    web_url = f"{GAME_URL}?user_id={user.id}&name={name}"
    await callback.answer(url=web_url)


# 3. WebApp'dan natija kelganda Telegram Game API ga saqlash
@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        score = int(data.get("score", 0))
        user = message.from_user
        user_name = f"@{user.username}" if user.username else user.first_name

        # Telegram High Scores (Game API) bazasiga saqlash
        await bot.set_game_score(
            user_id=user.id,
            score=score,
            chat_id=message.chat.id,
            message_id=message.message_id,
            force=True
        )

        await message.answer(
            f"🎯 **Natija saqlandi!**\n"
            f"👤 O‘yinchi: **{user_name}**\n"
            f"🏆 Ball: **{score}**\n\n"
            f"Guruhdagi umumiy o‘rinlarni ko‘rish uchun `/top` deb yozing.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Score saqlashda xatolik: {e}")


# 4. Guruhdagi umumiy reyting (Leaderboard / Rating)
@dp.message(Command("top"))
async def top_scores_handler(message: types.Message):
    try:
        # Xabarga javob (reply) qilingan bo'lsa o'sha game_message_id olinadi
        target_msg_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id

        high_scores = await bot.get_game_high_scores(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            message_id=target_msg_id
        )

        if not high_scores:
            await message.answer("Ushbu chatda hali hech kim natija ko‘rsatgani yo‘q.")
            return

        leaderboard_text = "🏆 **GURUH REYTINGI (TOP O'YINCHILAR):**\n\n"
        for rank, entry in enumerate(high_scores, start=1):
            u = entry.user
            name = f"@{u.username}" if u.username else u.first_name
            leaderboard_text += f"{rank}. **{name}** — {entry.score} ball\n"

        await message.answer(leaderboard_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Top reyting xatosi: {e}")
        await message.answer(
            "Reytingni ko‘rish uchun `/top` buyrug‘ini bot yuborgan **O‘yin xabariga reply (javob)** qilib yuboring."
        )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot tayyor va 24/7 rejimda ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())