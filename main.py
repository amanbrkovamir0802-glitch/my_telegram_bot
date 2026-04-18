import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from googletrans import Translator

# Bot tokenын усында қойың
BOT_TOKEN = "8662560813:AAHFsXWJUjLpIB8cxxoQ_fj5OphDgZ-Qny4"

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()

# Пайдаланыушының жазған текстин сақлаў ушын
user_texts = {}

# =============================================
# ТИЛЛЕР ДИЗИМИ (тил аты -> googletrans коды)
# =============================================
LANGUAGES = {
    "🏴 Қарақалпақша": "kaa",
    "🇬🇧 English":     "en",
    "🇷🇺 Русский":     "ru",
    "🇺🇿 O'zbek":      "uz",
    "🇰🇿 Қазақша":    "kk",
    "🇹🇷 Türkçe":      "tr",
    "🇩🇪 Deutsch":     "de",
    "🇫🇷 Français":    "fr",
    "🇪🇸 Español":     "es",
    "🇸🇦 العربية":     "ar",
    "🇨🇳 中文":         "zh-cn",
    "🇯🇵 日本語":       "ja",
    "🇰🇷 한국어":       "ko",
    "🇮🇹 Italiano":    "it",
    "🇵🇹 Português":   "pt",
    "🇮🇳 हिंदी":       "hi",
    "🇧🇩 বাংলা":       "bn",
    "🇮🇩 Indonesia":   "id",
    "🇳🇱 Nederlands":  "nl",
    "🇵🇱 Polski":      "pl",
    "🇸🇪 Svenska":     "sv",
    "🇳🇴 Norsk":       "no",
    "🇩🇰 Dansk":       "da",
    "🇫🇮 Suomi":       "fi",
    "🇬🇷 Ελληνικά":    "el",
    "🇨🇿 Čeština":     "cs",
    "🇷🇴 Română":      "ro",
    "🇭🇺 Magyar":      "hu",
    "🇺🇦 Українська":  "uk",
    "🇹🇭 ภาษาไทย":     "th",
    "🇻🇳 Tiếng Việt":  "vi",
    "🇵🇰 اردو":        "ur",
    "🇮🇷 فارسی":       "fa",
    "🇮🇱 עברית":       "he",
    "🇲🇾 Melayu":      "ms",
    "🇵🇭 Filipino":    "tl",
}


def build_language_keyboard():
    """3 тен кнопка болатуғын Inline клавиатура жасаў"""
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text=lang_name, callback_data=f"lang_{lang_code}")
        for lang_name, lang_code in LANGUAGES.items()
    ]
    markup.add(*buttons)
    return markup


# =============================================
# /start КОМАНДАСЫ
# =============================================
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Ассалаўма әлейкум! 👋\n\nАударма ислеў ушын сөз ямаса текст жазың:"
    )


# =============================================
# ПАЙДАЛАНЫУШЫ ТЕКСТ ЖАЗҒАНДА
# =============================================
@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    user_id = message.from_user.id
    user_texts[user_id] = message.text

    bot.send_message(
        message.chat.id,
        "Қайсы тилге аударма ислеў керек? 🌐",
        reply_markup=build_language_keyboard()
    )


# =============================================
# КНОПКА БАСЫЛҒАНДА (CALLBACK)
# =============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language_choice(call):
    user_id = call.from_user.id
    lang_code = call.data.replace("lang_", "")

    # Таңланған тил атын табыў
    lang_name = next(
        (name for name, code in LANGUAGES.items() if code == lang_code),
        lang_code
    )

    # Пайдаланыушы текстин алыў
    original_text = user_texts.get(user_id)

    if not original_text:
        bot.answer_callback_query(call.id, "⚠️ Әўели текст жазың!")
        bot.send_message(call.message.chat.id, "Аударма ислеў ушын текст жазың:")
        return

    # Аударма
    try:
        result = translator.translate(original_text, dest=lang_code)
        translated_text = result.text

        response = (
            f"📝 *Текст:* {original_text}\n"
            f"🌐 *Тил:* {lang_name}\n"
            f"✅ *Аударма:* {translated_text}"
        )

        # Қарақалпақ тилине аударма сапасы ҳаққында ескертиў
        if lang_code == "kaa":
            response += (
                "\n\n⚠️ _Диққет: Қарақалпақ тилине машина аудармасының сапасы "
                "толық дурыс болмаўы мүмкин. Нәтийжени тексерип шығыңыз._"
            )

        bot.answer_callback_query(call.id, "✅ Аударма tayır!")
        bot.send_message(
            call.message.chat.id,
            response,
            parse_mode="Markdown"
        )

    except Exception as e:
        # Қарақалпақ тили қоллап-қуўатланбаса, орысша аударып, ескертиў бериў
        if lang_code == "kaa":
            try:
                fallback = translator.translate(original_text, dest="ru")
                bot.answer_callback_query(call.id, "⚠️ Қарақалпақша аударма қол жетимли емес")
                bot.send_message(
                    call.message.chat.id,
                    f"📝 *Текст:* {original_text}\n"
                    f"🌐 *Тил:* {lang_name}\n\n"
                    f"⚠️ _Қарақалпақ тилине тікелей аударма қызмети ҳәзирше жетерли дәрежеде қол жетимли емес._\n\n"
                    f"💡 *Усыныс:* Орысша аударманы пайдаланыңыз:\n"
                    f"🇷🇺 *Орысша аударма:* {fallback.text}",
                    parse_mode="Markdown"
                )
            except Exception:
                bot.answer_callback_query(call.id, "❌ Қәте júz берди")
                bot.send_message(
                    call.message.chat.id,
                    "❌ Аударма ислеўде қәте júz берди. Қайтадан урынып көриң.",
                )
        else:
            bot.answer_callback_query(call.id, "❌ Қәте júz берди")
            bot.send_message(
                call.message.chat.id,
                f"❌ Аударма ислеўде қәте júz берди.\nҚайтадан урынып көриң немесе басқа тил таңлаң.\n\n_Қәте:_ `{str(e)}`",
                parse_mode="Markdown"
            )


# =============================================
# БОТТЫ ИСЛЕТИЎ
# =============================================
if __name__ == "__main__":
    print("🤖 Аударма боты жумысқа кирди...")
    bot.infinity_polling()
