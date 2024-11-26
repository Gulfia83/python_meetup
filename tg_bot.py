from email import message
import os
from random import choice

from datetime import date

import django
from django.utils.timezone import now
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
      CallbackContext, CallbackQueryHandler, PreCheckoutQueryHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_meetup.settings')
django.setup()

from python_meetup.settings import TG_BOT_TOKEN, PAY_MASTER_TOKEN

from bot.models import Donate, User, Program, Lecture

from bot_buttons_handler.show_programs import show_program
from bot_buttons_handler.donate import get_donation, confirm_donation, user_sum_for_donate,confirm_donation_custom, pre_checkout_callback, await_payment



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
    elif update.callback_query:
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
    if not context.bot_data['user'].name:
        return get_user_info(update, context)
    return make_networking(update, context)


def confirm_networking(update: Updater, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    elif update.callback_query.data == 'confirm':
        context.bot_data['user'].active = True
        context.bot_data['user'].save()
        return get_networking(update, context)


def get_user_info(update: Updater, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите ваше имя'
    )

    return 'GET_NAME'


def get_name(update: Updater, context: CallbackContext):
    message_text = update.message.text
    context.bot_data['user'].name = message_text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите название вашей компании'
    )
    return 'GET_COMPANY'


def get_company(update: Updater, context: CallbackContext):
    message_text = update.message.text
    context.bot_data['user'].company = message_text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите вашу должность'
    )
    return 'GET_POSITION'


def get_position(update: Updater, context: CallbackContext):
    message_text = update.message.text
    context.bot_data['user'].position = message_text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Сейчас я подберу вам собеседника'
    )
    return make_networking(update, context)


def make_networking(update: Updater, context: CallbackContext):
    active_users_count = User.objects.filter(active=True).count()
    keyboard = [
        [InlineKeyboardButton('Познакомиться',
                              callback_data='find_contact')] if active_users_count > 1 else [],
        [InlineKeyboardButton('Отказаться от участия',
                              callback_data='cancel_networking')],
        [InlineKeyboardButton('Главное меню',
                              callback_data='to_start')]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'''
        {context.bot_data['user'].name}, рады видеть вас в нетворкинге.
        Сейчас нас {active_users_count} человек''',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return 'NETWORK_COMMUNICATE'


def network_communicate(update: Updater, context: CallbackContext):
    data = update.callback_query.data
    if data == 'to_start':
        return start(update, context)
    elif data == 'cancel_networking':
        return cancel_networking(update, context)
    elif data == 'find_contact':
        return find_contact(update, context)


def cancel_networking(update: Updater, context: CallbackContext):
    context.bot_data['user'].active = False
    context.bot_data['user'].save
    return start(update, context)


def find_contact(update: Updater, context: CallbackContext):
    context.bot_data['networking'] = context.bot_data['user']
    while context.bot_data['networking'] == context.bot_data['user']:
        context.bot_data['networking'] = choice(
            User.objects.filter(active=True).exclude(tg_id=update.effective_chat.id)
        )

    keyboard = [
        [InlineKeyboardButton('Следующий контакт', callback_data='next_contact')],
        [InlineKeyboardButton('Отказаться от участия',
                              callback_data='cancel_networking')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'''
        {context.bot_data['networking'].name}
        {context.bot_data['networking'].position} в {context.bot_data['networking'].company}
        Связаться в Telegram:
        @{context.bot_data['networking'].tg_nick}
        ''',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return 'NEXT_CONTACT'


def next_contact(update: Updater, context: CallbackContext):
    data = update.callback_query.data
    if data == 'to_start':
        return start(update, context)
    elif data == 'cancel_networking':
        return cancel_networking(update, context)
    elif data == 'next_contact':
        return find_contact(update, context)


def handle_users_reply(update,
                       context,
                       ):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        username = update.message.from_user.username
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
        username = update.callback_query.from_user.username
    else:
        return
    user, created = User.objects.get_or_create(tg_id=chat_id,
                                               defaults={'tg_state': 'START',
                                                         'tg_nick': username})
    context.bot_data['user'] = user
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = context.bot_data['user'].tg_state
    states_functions = {
        'START': start,
        'CHOOSE_ACTION': choose_action,
        'CONFIRM_NETWORKING': confirm_networking,
        'GET_NAME': get_name,
        'GET_COMPANY': get_company,
        'GET_POSITION': get_position,
        'NETWORK_COMMUNICATE': network_communicate,
        'NEXT_CONTACT': next_contact,
        'CONFIRM_DONATION': confirm_donation,
        "CONFIRM_DONATION_CUSTOM": confirm_donation_custom,
        "AWAIT_PAYMENT": await_payment
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
    updater.dispatcher.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
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
