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
    if update.message:
        update.message.reply_text(
            'Добро пожаловать на наше мероприятие',
            reply_markup=reply_markup,
        )
    else:
        query = update.callback_query
        query.message.reply_text(
            'Выберите действие:',
            reply_markup=reply_markup,
        )
    
    return 'CHOOSE_ACTION'


def choose_action(update: Updater, context: CallbackContext):
    data = update.callback_query.data
    if data == 'my_questions':
        return get_questions(update, context)
    elif data == 'show_program':
        return show_program(update, context)
    elif data == 'add_question':
        return add_question(update, context)
    elif data == 'networking':
        return get_networking(update, context)
    elif data == 'make_donation':
        return get_donation(update, context)


def get_questions(update: Updater, context: CallbackContext):
    pass


def show_program(update: Updater, context: CallbackContext):
    pass


def add_question(update: Updater, context: CallbackContext):
    pass


def get_networking(update: Updater, context: CallbackContext):
    if context.bot_data['user'].active == False:
        keyboard = [
            [InlineKeyboardButton('Подтвердить участие',
                                  callback_data='confirm')],
            [InlineKeyboardButton('Главное меню',
                                  callback_data='to_start')]
        ]
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='''Вы можете пообщаться с другими участниками! Для этого\n
            нужно заполнить анкету и я подберу вам собеседника.\n
            Подтвердите участие.''',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return 'CONFIRM_NETWORKING'


def confirm_networking(update: Updater, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    elif update.callback_query.data == 'confirm':
        context.bot_data['user'].active = True
        context.bot_data['user'].save()
        return get_networking(update, context)


def get_user_info(update: Updater, context: CallbackContext):
    pass


def get_donation(update: Updater, context: CallbackContext):
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
    user, created = User.objects.get_or_create(tg_id=chat_id,
                                               defaults={'tg_state': 'START'})
    context.bot_data['user'] = user
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = context.bot_data['user'].tg_state
    states_functions = {
        'START': start,
        'CHOOSE_ACTION': choose_action,
        'CONFIRM_NETWORKING': confirm_networking,
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
