# from __future__ import print_function
import datetime
import json
import logging
import os
import random



import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils.request import Request

from ugc.models import GlobalNum
from ugc.models import Profile
from ugc.models import Register
from ugc.models import Pairs
from ugc.models import Quotes

BUTTON_ADD = 'Новая запись'
BUTTON_EDIT = 'Посмотреть заявки'
BUTTON_CHECK = 'ПОСМОТРЕТЬ ЗАЯВКИ'
BUTTON_1 = 'Срочно'
BUTTON_2 = 'По расписанию'
BUTTON_M = 'Мужской'
BUTTON_ZH = 'Женский'
BUTTON_NEW = 'Новая заявка'
BUTTON_YES = 'ДА'
BUTTON_NO = 'НЕТ'
BUTTON_EDIT_SUM_OPEN = 'Изменить цену открытия'
BUTTON_EDIT_TAKE_PROFIT = 'Изменить Тейк-профит'
BUTTON_EDIT_STOP_LOSS = 'Изменить стоп-лосс'
logger = logging.getLogger(__name__)
PAIRS = {'EURUSD': ['1', '12'],
         'AUDUSD': ['23', '12'],

         }

# for i in PAIRS:
#     print(i)

g = ' BRENT, indexUSD, GBPCAD, NZDUSD'
def get_base_check_keyboard():
    keyboard = [

            # [KeyboardButton('EURUSD')],
            # [KeyboardButton('AUDUSD')],
            # [KeyboardButton('GBPUSD')],
            # [KeyboardButton('EURGBP')],
            # [KeyboardButton('USDCHF')],
            # [KeyboardButton('XAUUSD')],
            # [KeyboardButton('XAGUSD')],
            # [KeyboardButton('USDCAD')],
            # [KeyboardButton('EURJPY')],
            # [KeyboardButton('EURCAD')],
            # [KeyboardButton('GBPJPY')],
            # [KeyboardButton('CHFJPY')],
            # [KeyboardButton('USDJPY')],
            # [KeyboardButton('BRENT')],
            # [KeyboardButton('indexUSD')],
            # [KeyboardButton('GBPCAD')],
            # [KeyboardButton('NZDUSD')],

    ]
    for i in Pairs.objects.all():
        keyboard.append([KeyboardButton(i.pair)])
    return ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)




def get_base_keyboard():
    keyboard = [

        [InlineKeyboardButton(BUTTON_ADD, callback_data='add')],
        [InlineKeyboardButton(BUTTON_EDIT, callback_data='edit')],

    ]
    return InlineKeyboardMarkup(keyboard)


def get_base_inline_new_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_YES, callback_data='yes_send'),
            InlineKeyboardButton(BUTTON_NO, callback_data='no_send'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_base_new_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON_YES),
            KeyboardButton(BUTTON_NO),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard = True)

def get_base_gender_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON_CHECK),

        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard = True)

def log_errors(f):

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            logger.error(error_message)
            raise e
    return inner


@log_errors
def do_edit(update: Update, context: CallbackContext):
    chat_id         = update.effective_chat.id

    keyboard = []
    for reg in Register.objects.all():
        keyboard.append([InlineKeyboardButton(f'{reg.сurrency_pair} '
                 f'{reg.sum_open} '
                 f'{reg.take_profit} '
                 f'{reg.stop_loss} ', callback_data=f'{reg.id}')])
    context.bot.send_message(chat_id=chat_id,
                             text='Регистрации',
                             reply_markup=InlineKeyboardMarkup(keyboard))


@log_errors
def do_add(update: Update, context: CallbackContext):
    chat_id             = update.effective_chat.id
    profile = Profile.objects.get(external_id=chat_id)
    profile.numQuestionProfile = 1
    profile.save()
    reg = Register.objects.create()
    context.bot.send_message(
        chat_id      = chat_id,
        text         = '1. Валютная Пара:',
        reply_markup = get_base_check_keyboard(),
    )

@log_errors
def do_start(update: Update, context: CallbackContext):
    chat_id             = update.effective_chat.id
    logger.info(f'-----do_start-----')
    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={'name': update.message.from_user.username,
                  }
    )
    context.bot.send_message(
        chat_id=chat_id,
        text='👋',
        reply_markup=get_base_keyboard(),
    )

@log_errors
def do_check(update: Update, context: CallbackContext):
    logger.info(f'-----do_check-----')
    chat_id             = update.message.chat_id
    text                = update.message.text

    reg = Register.objects.last()
    profile = Profile.objects.get(external_id=chat_id)
    if profile.changedOfProfile == 'ДА':
        reg = Register.objects.get(id = profile.changedThatIdOfProfile)
        if profile.changedThatOfProfile == 'sum_open':
            logger.info(f'---изменяем sum_open---')
            reg.take_profit = text
            reg.save()
            context.bot.send_message(
                chat_id=chat_id,
                text='Успешно сохранено',

            )
            profile.changedOfProfile = 'НЕТ'
            profile.save()
            do_edit(update=update, context=context)
            pass
        if profile.changedThatOfProfile == 'take_profit':
            logger.info(f'---изменяем take_profit---')
            reg.take_profit = text
            reg.save()
            context.bot.send_message(
                chat_id=chat_id,
                text='Успешно сохранено',

            )
            profile.changedOfProfile = 'НЕТ'
            profile.save()
            do_edit(update=update, context=context)
            pass
        if profile.changedThatOfProfile == 'stop_loss':
            logger.info(f'---изменяем stop_loss---')
            reg.take_profit = text
            reg.save()
            context.bot.send_message(
                chat_id=chat_id,
                text='Успешно сохранено',

            )
            profile.changedOfProfile = 'НЕТ'
            profile.save()
            do_edit(update=update, context=context)
            pass

    if text == BUTTON_YES:

        logger.info(f'---Отправляем в каналы---')
        logger.info('🚨\n'
                 f'\nВалютная пара: {reg.сurrency_pair}'
                 f'\nЦена открытия: {reg.sum_open}'
                 f'\nТейк-профит: {reg.take_profit}'
                 f'\nСтоп-лосс: {reg.stop_loss}')
        context.bot.send_message(
            chat_id=-1001194041050,
            text='🚨\n'
                 f'\nВалютная пара: {reg.сurrency_pair}'
                 f'\nЦена открытия: {reg.sum_open}'
                 f'\nТейк-профит: {reg.take_profit}'
                 f'\nСтоп-лосс: {reg.stop_loss}',
        )
        context.bot.send_message(
            chat_id=chat_id,
            text='Отправляю...',
            reply_markup=get_base_keyboard()
        )

    elif text == BUTTON_NO:
        context.bot.send_message(
            chat_id=chat_id,
            text='Хорошо, сохранил в базе',
            reply_markup=get_base_keyboard()
        )
    if profile.numQuestionProfile == 1:
        keyboard =[]
        for quote in Quotes.objects.filter(pair = Pairs.objects.get(pair = text)):
            keyboard.append([KeyboardButton(quote.quote)])
        context.bot.send_message(
            chat_id=chat_id,
            text='Цена открытия',
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)
        )
        profile.numQuestionProfile += 1
        reg.сurrency_pair = text
        profile.save()
        reg.save()
    elif profile.numQuestionProfile == 2:
        try:
            if Quotes.objects.get(pair = Pairs.objects.get(pair = reg.сurrency_pair), quote = text).is_full == True:
                context.bot.send_message(
                    chat_id=chat_id,
                    text='Дописывайте'
                )
                reg.sum_open = text
                reg.save()
            else:
                context.bot.send_message(
                    chat_id=chat_id,
                    text='Тейк-профит'
                )
                profile.numQuestionProfile += 1
                reg.sum_open = text
                profile.save()
                reg.save()
        except Quotes.DoesNotExist:
            context.bot.send_message(
                chat_id=chat_id,
                text='Тейк-профит'
            )
            profile.numQuestionProfile += 1
            reg.sum_open += text
            profile.save()
            reg.save()
    elif profile.numQuestionProfile == 3:
        context.bot.send_message(
            chat_id=chat_id,
            text='Стоп-лосс'
        )
        profile.numQuestionProfile += 1
        reg.take_profit = text
        profile.save()
        reg.save()
    elif profile.numQuestionProfile == 4:

        profile.numQuestionProfile += 1
        reg.stop_loss = text
        profile.save()
        reg.save()
        context.bot.send_message(
            chat_id=chat_id,
            text='🚨\n'
                 f'\nВалютная пара: {reg.сurrency_pair}'
                 f'\nЦена открытия: {reg.sum_open.replace("+", "")}'
                 f'\nТейк-профит: {reg.take_profit}'
                 f'\nСтоп-лосс: {reg.stop_loss}',
            reply_markup=get_base_new_keyboard()
        )
        # -1001194041050
        context.bot.send_message(
            chat_id=chat_id,
            text='Отправить в каналы?',
            reply_markup=get_base_new_keyboard()
        )


# @log_errors
# def do_questions(update: Update, context: CallbackContext):
#     chat_id = update.message.chat_id
#     text = update.message.text
#     profile = Profile.objects.get(external_id=chat_id)
#
# @log_errors
# def do_check_register(update: Update, context: CallbackContext):
#
#     chat_id   = update.message.chat_id
#     profile   = Profile.objects.get(external_id=chat_id)
#     keyboard =[]
#     for i in Register.objects.all():
#         keyboard.append([InlineKeyboardButton(f'{i.сurrency_pair}', callback_data=i.id)])
#     context.bot.send_message(chat_id=chat_id,
#                                  text='Регистрации',
#                              reply_markup=keyboard)

@log_errors
def keyboard_callback_handler(update: Update, context: CallbackContext):
    query                     = update.callback_query
    data                      = query.data
    chat_id         = update.effective_chat.id
    profile = Profile.objects.get(external_id=chat_id)

    if data == 'add':
        do_add(update=update, context=context)
    elif data == 'edit':

        do_edit(update=update, context=context)
    elif data == 'yes_send':

        if profile.typeOfProfile != 'Не определился':
            reg = Register.objects.get(id=profile.typeOfProfile)
            context.bot.send_message(
                chat_id=-1001194041050,
                text='🚨\n'
                     f'\nВалютная пара: {reg.сurrency_pair}'
                     f'\nЦена открытия: {reg.sum_open}'
                     f'\nТейк-профит: {reg.take_profit}'
                     f'\nСтоп-лосс: {reg.stop_loss}',
            )
            context.bot.send_message(
                chat_id=chat_id,
                text='Отправил',
                reply_markup=get_base_keyboard()
            )
        profile.typeOfProfile = 'Не определился'
        profile.save()
    elif data == 'no_send':
        context.bot.send_message(
            chat_id=chat_id,
            text='Хорошо',
            reply_markup=get_base_keyboard()
        )
    elif 'edit_' in data:
        profile.changedOfProfile = 'ДА'
        res = data.split('[]')
        profile.changedThatOfProfile = res[2]
        profile.changedThatIdOfProfile = res[1]
        profile.save()
        if res[2] == 'sum_open':
            keyboard = []
            for quote in Quotes.objects.filter(pair=Pairs.objects.get(pair=Register.objects.get(id=res[1]).сurrency_pair)):
                keyboard.append([KeyboardButton(quote.quote.replace('+', ''))])
            context.bot.send_message(
                chat_id=chat_id,
                text='Введите обновленное значение:',
                reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)
            )
        else:
            context.bot.send_message(
                chat_id=chat_id,
                text='Введите обновленное значение:',
            )

    else:


       profile.typeOfProfile = data
       profile.save()
       reg =  Register.objects.get(id = data)
       context.bot.send_message(
           chat_id=chat_id,
           text='🚨\n'
                f'\nВалютная пара: {reg.сurrency_pair}'
                f'\nЦена открытия: {reg.sum_open}'
                f'\nТейк-профит: {reg.take_profit}'
                f'\nСтоп-лосс: {reg.stop_loss}',
       )
       keyboard = [
           [
               InlineKeyboardButton(BUTTON_YES, callback_data='yes_send'),
               InlineKeyboardButton(BUTTON_NO, callback_data='no_send'),


           ],
           [InlineKeyboardButton(BUTTON_EDIT_SUM_OPEN, callback_data=f'edit_[]{reg.id}[]sum_open')],
           [InlineKeyboardButton(BUTTON_EDIT_TAKE_PROFIT, callback_data=f'edit_[]{reg.id}[]take_profit')],
           [InlineKeyboardButton(BUTTON_EDIT_STOP_LOSS, callback_data=f'edit_[]{reg.id}[]stop_loss')],
       ]

       # -1001194041050
       context.bot.send_message(
           chat_id=chat_id,
           text='Отправить в каналы?',
           reply_markup=InlineKeyboardMarkup(keyboard)
       )
class Command(BaseCommand):
    help = 'Телеграм - бот'




    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(request=request,
                  token=settings.TOKEN)
        logger.info(bot.get_me())

        updater = Updater(bot = bot,
                          use_context=True)
        start_handler = CommandHandler('start', do_start)
        add_handler = CommandHandler('add', do_add)
        message_handler = MessageHandler(Filters.text, do_check)
        buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler, pass_chat_data=True)
        updater.dispatcher.add_handler(add_handler)
        updater.dispatcher.add_handler(start_handler)

        updater.dispatcher.add_handler(message_handler)
        updater.dispatcher.add_handler(buttons_handler)


        updater.start_polling()
        updater.idle()

