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

def add_question(update: Updater, context: CallbackContext):
    pass

#!-----------------------------------------------------------------------------------------
def get_donation(update: Updater, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('50 ₽', callback_data='donate_50')],
        [InlineKeyboardButton('100 ₽', callback_data='donate_100')],
        [InlineKeyboardButton('500 ₽', callback_data='donate_500')],
        [InlineKeyboardButton('Ввести свою сумму', callback_data='user_donate')],
        [InlineKeyboardButton('Назад', callback_data='to_start')],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы можете помочь нам финансово. Выберите сумму доната:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return "CONFIRM_DONATION"



def confirm_donation(update: Updater, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id

    if update.callback_query.data == 'to_start':
        return start(update, context)
    if update.callback_query.data == 'user_donate':
        return user_sum_for_donate(update, context)


    if data.startswith("donate_"):
        amount = int(data.split("_")[1])
        prices = [LabeledPrice(label=f"Донат на сумму {amount} ₽", amount=amount * 100)]

        context.bot.send_invoice(
            chat_id=chat_id,
            title="Донат на поддержку",
            description=f"Спасибо за ваше желание поддержать наш проект на {amount} ₽!",
            payload=f"donation_{amount}",
            provider_token=PAY_MASTER_TOKEN,
            currency="RUB",
            prices=prices,
            start_parameter="donation",
        )
        return "AWAIT_PAYMENT"

    if data == "to_start":
        return start(update, context)


def user_sum_for_donate(update: Updater, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите желаемую сумму пожертования'
    )

    return "CONFIRM_DONATION_CUSTOM"


def confirm_donation_custom(update: Updater, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_text = update.message.text

    amount = int(message_text)
    prices = [LabeledPrice(label=f"Донат на сумму {amount} ₽", amount=amount * 100)]

    context.bot.send_invoice(
    chat_id,
    title="Донат на поддержку",
    description=f"Спасибо за ваше желание поддержать наш проект на {amount} ₽!",
    payload=f"donation_{amount}",
    provider_token=PAY_MASTER_TOKEN,
    currency="RUB",
    prices=prices,
    start_parameter="donation",
    )
    return "AWAIT_PAYMENT"

def await_payment(update: Updater, context: CallbackContext):
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    amount = int(payment.total_amount) / 100

    user, _ = User.objects.get_or_create(
        telegram_id=update.effective_user.id, defaults={"name": update.effective_user.first_name}
    )
    Donate.objects.create(user=user, amount=amount, donated_at=now())

    update.message.reply_text(
        f"Спасибо за ваш донат на сумму {amount:.2f} ₽! 🙏",
        parse_mode=ParseMode.HTML,
    )
    return start(update, context)


def pre_checkout_callback(update: Updater, context: CallbackContext):
    query = update.pre_checkout_query

    if query.invoice_payload.startswith("donation_"):
        query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Некорректный payload. Попробуйте снова.")
#!-----------------------------------------------------------------------------------------


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
        "AWAIT_PAYMENT": await_payment,
        "CONFIRM_DONATION_CUSTOM": confirm_donation_custom,
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
