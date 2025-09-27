# bot.py
import os
import logging
from dotenv import load_dotenv
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# load .env in local dev; Railway will use env vars set in its dashboard
load_dotenv()

TELEGRAM_TOKEN = os.getenv("8364249900:AAHwMq2PDpIUATHHoBsNyBgvc8GgbnMeqso")
OPENAI_API_KEY = os.getenv("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")
CREATOR_USERNAME = os.getenv("CREATOR_USERNAME", "your_username_here")  # set this in env vars

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("Please set TELEGRAM_TOKEN and OPENAI_API_KEY environment variables.")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = "سلام! من یک ربات هوش مصنوعی هستم — هر سوالی داشتی بپرس 🙂"
    # دکمه ارتباط با سازنده
    keyboard = [
        [InlineKeyboardButton("تماس با سازنده", url=f"https://t.me/AIireza_1383")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, reply_markup=reply_markup)

async def ask_openai(prompt: str) -> str:
    """ارسال prompt به OpenAI و دریافت پاسخ"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # یا مدل دلخواهی که در حساب شما موجود است
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers in Persian."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            n=1,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("OpenAI request failed")
        return "متاسفم — مشکلی در ارتباط با سرویس هوش مصنوعی پیش آمد."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # کوتاه‌سازی ساده در صورت نیاز
    if not user_text or user_text.strip() == "":
        await update.message.reply_text("لطفاً یک پیام متنی بفرستید.")
        return

    # نشان به کاربر که در حال پردازش است
    sent = await update.message.reply_text("در حال فکر کردن...")

    # درخواست به OpenAI
    answer = await ask_openai(user_text)
    # ویرایش پیام (یا ارسال پیام جدید)
    try:
        await sent.edit_text(answer)
    except:
        await update.message.reply_text(answer)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # start polling (ساده‌ترین روش؛ Railway هم معمولاً این حالت را پشتیبانی می‌کند).
    # مستندات python-telegram-bot درباره polling/webhook را ببینید. :contentReference[oaicite:3]{index=3}
    app.run_polling()

if __name__ == "__main__":
    main()


