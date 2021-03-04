# from __future__ import print_function
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardRemove
from telegram.utils.request import Request
from ugc.models import Profile
from ugc.models import Questions
from ugc.models import Answer
from ugc.models import GlobalNum
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
import pandas as pd
import os
from oauth2client import tools
import pygsheets
import dropbox
import datetime
from pathlib import Path
import random
from datetime import timedelta

BUTTON_1 = 'Срочно'
BUTTON_2 = 'По расписанию'
BUTTON_M = 'Мужской'
BUTTON_ZH = 'Женский'
BUTTON_NEW = 'Новая заявка'

def get_base_check_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON_1),
            KeyboardButton(BUTTON_2),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_base_new_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON_NEW),

        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard = True)

def get_base_gender_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON_M),
            KeyboardButton(BUTTON_ZH),
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
            raise e
    return inner



@log_errors
def do_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    print(chat_id)

    context.bot.send_message(
        chat_id=chat_id,
        text='Для регистрации укажите уровень срочности обслуживания',
        reply_markup=get_base_check_keyboard(),
    )

    # p, _ = Profile.objects.get_or_create(
    #     external_id=chat_id,
    #     defaults={'name': update.message.from_user.username,
    #               }
    # )
    # profile = Profile.objects.get(external_id=chat_id)
    # context.bot.send_message(
    #     chat_id=profile.external_id,
    #     text=f'{Questions.objects.get(numQuestion=profile.numQuestionProfile).question}:'
    # )

@log_errors
def do_check(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    p, _ = Profile.objects.get_or_create(
            external_id=chat_id,
            defaults={'name': update.message.from_user.username,
                      }
        )
    profile = Profile.objects.get(external_id=chat_id)
    print(text)
    if profile.numQuestionProfile > 3:
        profile.numQuestionProfile = 1
        profile.save()
        do_check(update=update, context=context)
    elif text == 'Новая заявка':
        answers = Answer.objects.all().filter(respondentId=profile.external_id)
        answers.delete()
        return do_start(update=update, context=context,)
    elif text == 'Срочно':
        profile.typeOfProfile = 'Срочно'
        profile.save()
        return do_questions(update=update, context=context,)
    elif text == 'По расписанию':
        profile.typeOfProfile = 'По расписанию'
        profile.save()
        return do_questions(update=update, context=context,)
    elif profile.typeOfProfile == 'Не определился':
        return do_start(update=update, context=context)
    else:
        answer = Answer.objects.create(
            dateAnswer = update.message.date,
            respondentId=chat_id,
            numAnswer=profile.numQuestionProfile,
            textAnswer = text,

        )
        answer.save()
        profile.numQuestionProfile += 1
        profile.save()
        do_questions(update=update, context=context,)





@log_errors
def do_questions(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    profile = Profile.objects.get(external_id=chat_id)
    if profile.numQuestionProfile > 3:
        # answer = Answer.objects.create(
        #     dateAnswer=update.message.date,
        #     respondentId=chat_id,
        #     numAnswer=profile.numQuestionProfile,
        #     textAnswer=text,
        #
        # )
        num = GlobalNum.objects.get(gnum=1)
        num.num += 1
        num.save()
        # выгрузка
        randomNum = random.randint(1, 9999999999)
        print(1)
        gDocs(update=update, context=context, profile=profile, randomNum=randomNum)

        if profile.typeOfProfile == 'Срочно':
            context.bot.send_message(
                chat_id = -466305201,
                text= f'ВНИМАНИЕ! Срочная заявка от {update.message.from_user.username}'
            )
        elif profile.typeOfProfile == 'По расписанию':
            context.bot.send_message(
                chat_id=-466305201,
                text=f'Новая заявка от {update.message.from_user.username}'
            )
            pass
        profile.numQuestionProfile = 1
        profile.typeOfProfile = 'Не определился'
        profile.save()
        context.bot.send_message(chat_id=chat_id,
                                 text=f'«Заявка №{randomNum} принята. Ваш координатор отправит готовый результат в установленные сроки',
                                 reply_markup=get_base_new_keyboard())


    elif Questions.objects.get(numQuestion=profile.numQuestionProfile).question == 'Укажите пол':
        context.bot.send_message(
            chat_id=profile.external_id,
            text=f'{Questions.objects.get(numQuestion=profile.numQuestionProfile).question}:',
            reply_markup=get_base_gender_keyboard()
        )
    else:
        context.bot.send_message(
            chat_id=profile.external_id,
            text=f'{Questions.objects.get(numQuestion=profile.numQuestionProfile).question}:',
            reply_markup=ReplyKeyboardRemove(get_base_check_keyboard())
        )



# @log_errors
# def do_photo(update: Update, context: CallbackContext):
#
#     chat_id = update.message.chat_id
#     profile = Profile.objects.get(external_id=chat_id)
#     print(update.message)
#     photoFile = context.bot.get_file(update.message.photo[-1].file_id)
#     path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
#     path = os.path.join(path, 'photos', f'profile_{chat_id}_answer_{profile.numQuestionProfile}_.jpg')
#     # path = f'./photos/profile_{chat_id}_answer_{profile.numQuestionProfile}_.jpg'
#     context.bot.send_message(chat_id=chat_id,
#                                  text='Сохраняем ваше фото...',)
#     photoFile.download(path)
#
#     dbx = dropbox.Dropbox('V1Lt6QGymxYAAAAAAAAAAewFSct5TfwVqOsn1MJwYgkmO___22SBHlWRL_pQJrZO')
#     photo_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
#     photo_path = os.path.join(photo_path, 'photos',f'profile_{profile.external_id}_answer_3_.jpg')
#
#     with open(photo_path,
#               'rb') as file:
#         response = dbx.files_upload(file.read(),
#                                     f'/myfile{GlobalNum.objects.get(gnum=1).num}.jpg')  # загружаем файл: первый аргумент (file.read()) - какой файл; второй - название, которое будет присвоено файлу уже на дропбоксе.
#         print(response)  # выводим результат загрузки
#
#     answer = Answer.objects.create(
#         dateAnswer=update.message.date,
#         respondentId=chat_id,
#         numAnswer=profile.numQuestionProfile,
#         textAnswer=dbx.sharing_create_shared_link(f'/myfile{GlobalNum.objects.get(gnum=1).num}.jpg').url,
#
#     )
#     num = GlobalNum.objects.get(gnum=1)
#     num.num +=1
#     num.save()
#     answer.save()
#     # выгрузка
#     randomNum = random.randint(1, 9999999999)
#     gDocs(update=update, context=context, profile=profile, randomNum=randomNum)
#
#     profile.numQuestionProfile = 1
#     profile.typeOfProfile = 'Не определился'
#     profile.save()
#     context.bot.send_message(chat_id=chat_id,
#                              text=f'«Заявка №{randomNum} принята. Ваш координатор отправит готовый результат в установленные сроки',
#                              reply_markup=get_base_new_keyboard())
#

@log_errors
def gDocs(profile, update: Update, context: CallbackContext, randomNum):

    data = serialize('json', Answer.objects.all().filter(respondentId=profile.external_id),
                     cls=DjangoJSONEncoder)
    maindata = {}
    data = json.loads(data)
    maindata['name'] = data[0]['fields']['textAnswer']
    maindata['birthrday'] = data[1]['fields']['textAnswer']
    maindata['age'] = ((datetime.datetime.now() + datetime.timedelta(hours=3, minutes=0)) - (datetime.datetime.strptime(data[1]['fields']['textAnswer'], '%d.%m.%Y'))).days // 365
    maindata['numrandom'] = randomNum
    maindata['fiveCode'] = random.randint(1, 99999)
    maindata['gender'] = data[2]['fields']['textAnswer']
    maindata['twoDays1'] = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%d.%m.%Y')
    maindata['twoDays2'] = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%d.%m.%Y')
    maindata['oneDay'] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
    maindata['date'] = (datetime.datetime.now() + datetime.timedelta(hours=3, minutes=0)).strftime("%d.%m.%Y")
    maindata['time'] = (datetime.datetime.now() + datetime.timedelta(hours=3, minutes=0)).strftime("%H:%M:%S")
    print(1)
    maindata['Svoi6'] = ''
    maindata['Svoi7'] = ''
    maindata['user_name'] = update.message.from_user.username
    maindata['typeOfProfile'] = profile.typeOfProfile

    # print(11)
    #
    # print(1)
    #
    # maindata['oneDay'] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
    #
    # print(data)
    #
    # print(data[1]['fields']['textAnswer'])
    # for i in data:
    #     maindata[i['fields']['numAnswer']] = i['fields']['textAnswer'];

    df = pd.DataFrame(data=[maindata])
    script_directory = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_directory, 'amocrmsheets-3d5c4cc53e73.json')
    gh = GSheets(json_file, file_url='https://docs.google.com/spreadsheets/d/1nO6frE5qidy1GMXbRlbBUVMqyC_0g7qpPoRPxdSyTPw/edit?usp=sharing')
    gh.add_df_to_sheets(df=df, sheetname='Лист1')

    answers = Answer.objects.all().filter(respondentId=profile.external_id)
    answers.delete()

class GSheets:

    def __init__(self,service_file,filename='',file_url=''):
        if service_file:
            gc = pygsheets.authorize(service_file=service_file)
        else:
            gc = pygsheets.authorize()
        if filename!='':
            sh = gc.open(filename)
        elif file_url!='':
            sh = gc.open_by_url(file_url)
        else:
            #logger.info('name and url is empty')
            return False

        self.service_file = service_file
        self.filename = filename
        self.gc = gc
        self.sh = sh
        pass
    # сохранение данных в таблицу
    def set_df_to_sheets(self, sheetname, df):
        wks = self.sh.worksheet_by_title(sheetname)
        wks.clear()
        wks.set_dataframe(df, (1, 1),fit=True,nan='')
        #logger.info(f'Save: {sheetname}')
        return df
    # получение данных и таблицы
    def get_df_to_sheets(self, sheetname):
        wks = self.sh.worksheet_by_title(sheetname)

        df= wks.get_as_df()
        #logger.info(f'Load: {sheetname}')
        return df
    # добавление данных в таблицу
    def add_df_to_sheets(self, sheetname, df):
        wks = self.sh.worksheet_by_title(sheetname)
        #wks.clear()
        wks.insert_rows(1, number=len(df), values=None, inherit=False)
        wks.set_dataframe(df, (2, 1),nan='',copy_head=False)
        #logger.info(f'Add: {sheetname}')
        return df


class Command(BaseCommand):
    help = 'Телеграм - бот'




    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(request=request,
                  token=settings.TOKENDEBUG)
        print(bot.get_me())

        updater = Updater(bot = bot,
                          use_context=True)
        start_handler = CommandHandler('start', do_start)
        message_handler = MessageHandler(Filters.text, do_check)
        # photo_handler = MessageHandler(Filters.photo, do_photo)
        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(message_handler)
        # updater.dispatcher.add_handler(photo_handler)


        updater.start_polling()
        updater.idle()



