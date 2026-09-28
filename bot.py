import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# O'zgaruvchilarni olish (Railway Environment Variables yoki to'g'ridan-to'g'ri string)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8837550445:AAHf07Q7EooDoyObC8reK8A_F2GkBaFV2Nw")
GAME_URL = os.getenv("GAME_URL", "math-battle-reverse-2z1fqmcws-lynx-fb43.vercel.app/index.html")
GAME_SHORT_NAME = "math_battle_reverse"  # BotFather'dan o'yinga bergan short_name ingiz

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# 1. Start va Game yuborish
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Foydalanuvchi yoki guruhga o'yin xabarini yuborish."""
    await bot.send_game(
        chat_id=message.chat.id,
        game_short_name=GAME_SHORT_NAME
    )


# 2. O'yinni boshlash tugmasi bosilganda (CallbackQuery)
@dp.callback_query(F.game_short_name)
async def game_callback_handler(callback: types.CallbackQuery):
    """
    O'yinchiga HTML5 o'yin havolasini (Vercel URL) ochib beradi.
    Telegram Game API uchun url callback.game_short_name bilan mos bo'lishi kerak.
    """
    await callback.answer(url=f"{GAME_URL}?user_id={callback.from_user.id}")


# 3. WebApp'dan kelgan natijani qabul qilish va Telegram Game API'ga saqlash
@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    """
    index.html'dan Telegram.WebApp.sendData() orqali kelgan natijani (score)
    Telegram serveriga saqlash va guruhda e'lon qilish.
    """
    import json
    try:
        data = json.loads(message.web_app_data.data)
        score = int(data.get("score", 0))

        user = message.from_user
        user_display_name = f"@{user.username}" if user.username else user.first_name

        # Telegram Game API'ga ochkoni saqlaymiz
        await bot.set_game_score(
            user_id=user.id,
            score=score,
            chat_id=message.chat.id,
            message_id=message.message_id,
            force=True
        )

        await message.answer(
            f"🎮 **O‘yin tugadi!**\n"
            f"👤 O‘yinchi: **{user_display_name}**\n"
            f"🏆 Natija: **{score} ball**",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Score saqlashda xatolik: {e}")


# 4. Guruhdagi umumiy reytingni (Leaderboard) ko'rsatish
@dp.message(Command("top"))
async def top_scores_handler(message: types.Message):
    """
    Guruhdagi eng yuqori natijaga ega o'yinchilar ro'yxatini chiqaradi.
    Eslatma: Bu buyruq o'yin xabariga 'Reply' qilib yuborilganda yoki guruhda ishlaydi.
    """
    try:
        # Agar xabarga reply qilingan bo'lsa, o'sha xabarning message_id si olinadi
        target_message_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id

        high_scores = await bot.get_game_high_scores(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            message_id=target_message_id
        )

        if not high_scores:
            await message.answer("Ushbu chatda hali hech kim natija ko‘rsatgani yo‘q.")
            return

        leaderboard_text = "🏆 **Guruhdagi eng yaxshi natijalar:**\n\n"
        for rank, entry in enumerate(high_scores, start=1):
            u = entry.user
            name = f"@{u.username}" if u.username else u.first_name
            leaderboard_text += f"{rank}. {name} — **{entry.score}** ball\n"

        await message.answer(leaderboard_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Top natijalarni olishda xatolik: {e}")
        await message.answer(
            "Natijalarni ko‘rish uchun `/top` buyrug‘ini bot yuborgan **O‘yin xabariga reply** (javob) qilib yuboring."
        )


# Botni ishga tushirish funksiyasi
async def main():
    # Eski Webhook va kelib tushgan ortiqcha so'rovlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot 24/7 rejimida ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())