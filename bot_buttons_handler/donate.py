from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from python_meetup.settings import PAY_MASTER_TOKEN

from bot.models import User

def get_donation(update: Updater, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('Пожертвовать',
                                callback_data='confirm')],
        [InlineKeyboardButton('Назад',
                                callback_data='to_start')]
    ]
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='''Вы можете помочб нам финансово, если хотите.''',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return "CONFIRM_DONATION"
