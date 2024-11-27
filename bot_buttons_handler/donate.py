
from django.utils.timezone import now
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Updater, CallbackContext


from python_meetup.settings import PAY_MASTER_TOKEN

from bot.models import Donate, User, Donate


def get_donation(update: Updater, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('50 ₽', callback_data='donate_50')],
        [InlineKeyboardButton('100 ₽', callback_data='donate_100')],
        [InlineKeyboardButton('500 ₽', callback_data='donate_500')],
        [InlineKeyboardButton('Ввести свою сумму', callback_data='user_donate')],
        [InlineKeyboardButton('Назад', callback_data='to_start')],
    ]
    query = update.callback_query
    query.edit_message_text(
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
        return "START"


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

def pre_checkout_callback(update: Updater, context: CallbackContext):
    query = update.pre_checkout_query
    payload = query.invoice_payload
    amount = int(payload.split("_")[1])

    if query.invoice_payload.startswith("donation_"):
        query.answer(ok=True)
        user, _ = User.objects.get_or_create(
        tg_id=update.effective_user.id, defaults={"tg_nick": update.effective_user.first_name}
        )
        Donate.objects.create(user=user, amount=amount, donated_at=now())
        user = context.bot_data['user']
        user.tg_state = 'START'
        user.save()

    else:
        query.answer(ok=False, error_message="Некорректный payload. Попробуйте снова.")


def await_payment(update: Updater, context: CallbackContext):
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='''Платеж прошел успешно!''',
        )
    return "START"
