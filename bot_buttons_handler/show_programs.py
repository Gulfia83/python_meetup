from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, Updater

from bot.models import Program


def show_program(update: Updater, context: CallbackContext):
    today = date.today()
    program_today = (
        Program.objects.filter(date=today).prefetch_related("lectures").first()
    )

    if not program_today:
        update.callback_query.message.reply_text(
            "На сегодня программ не запланировано."
        )
        return "BACK_TO_MENU"

    text = "Программа на сегодня:\n\n"
    text += f"<b><i>{program_today.name}</i></b>\n\n"
    for lecture in program_today.lectures.all():
        text += f" <i>{lecture.speaker.name} - {lecture.name}</i> (с {lecture.start_time:%H:%M} \
            до {lecture.end_time:%H:%M})\n {lecture.description}\n ━━━━━━━━━━━━ \n\n"

    update.callback_query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Главное меню", callback_data="to_start")]]
        ),
        parse_mode=ParseMode.HTML,
    )

    return "START"
