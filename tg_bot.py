import os

import django
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
      CallbackContext, CallbackQueryHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_meetup.settings')
django.setup()

from python_meetup.settings import TG_BOT_TOKEN
from bot.models import User


def start(update: Updater, context: CallbackContext):

    keyboard = [
        [InlineKeyboardButton('Вопросы ко мне',
                              callback_data='my_questions')] if context.bot_data['user'].status == 'SPEAKER' else [],
        [InlineKeyboardButton('Программа',
                              callback_data='show_program'),
         InlineKeyboardButton('Задать вопрос спикеру',
                              callback_data='add_question')],
        [InlineKeyboardButton('Хочу познакомиться',
                              callback_data='networking'),
         InlineKeyboardButton('Задонатить',
                              callback_data='make_donation')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Добро пожаловать на наше мероприятие',
        reply_markup=reply_markup,
    )
    
    return 'CHOOSE_ACTION'


def choose_action(update: Updater, context: CallbackContext):
    pass


def handle_users_reply(update,
                       context,
                       ):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    user, created = User.objects.get_or_create(tg_id=chat_id)
    context.bot_data['user'] = user
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = user.tg_state
    states_functions = {
        'START': start,
        'CHOOSE_ACTION': choose_action,
        }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        context.bot_data['user'].tg_state = next_state
        context.bot_data['user'].save()
    except Exception as err:
        print(err)


def main() -> None:
    bot = Bot(TG_BOT_TOKEN)

    updater = Updater(TG_BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(
        MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(
        CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
