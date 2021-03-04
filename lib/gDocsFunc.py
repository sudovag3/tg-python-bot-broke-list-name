import json
import os
import random
from datetime import datetime

from django.conf import settings
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from telegram import Update
from telegram.ext import CallbackContext
import pandas as pd

from lib.gsheets_lib import GSheets
from lib.log_errors import log_errors
from tgOprosAdmin.ugc.models import Answer

@log_errors
def gDocs(profile, update: Update, context: CallbackContext, randomNum):

    data                        = serialize('json', Answer.objects.all().filter(respondentId=profile.external_id),
                                                            cls=DjangoJSONEncoder)
    maindata                    = {}
    data                        = json.loads(data)
    maindata['name']            = data[0]['fields']['textAnswer']
    maindata['birthrday']       = data[1]['fields']['textAnswer']
    maindata['age']             = ((datetime.datetime.now() + datetime.timedelta(hours=3, minutes=0)) - (datetime.datetime.strptime(data[1]['fields']['textAnswer'], '%d.%m.%Y'))).days // 365
    maindata['numrandom']       = randomNum
    maindata['fiveCode']        = random.randint(1, 99999)
    maindata['gender']          = data[2]['fields']['textAnswer']
    maindata['photo']           = data[3]['fields']['textAnswer']
    maindata['twoDays1']        = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%d.%m.%Y')
    maindata['twoDays2']        = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%d.%m.%Y')
    maindata['oneDay']          = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
    maindata['date']            = (datetime.datetime.now() + datetime.timedelta(hours=3, minutes=0)).strftime("%d.%m.%Y")
    maindata['time']            = (datetime.datetime.now() + datetime.timedelta(hours=3, minutes=0)).strftime("%H:%M:%S")
    maindata['user_name']       = update.message.from_user.username
    maindata['typeOfProfile']   = profile.typeOfProfile

    df               = pd.DataFrame(data=[maindata])
    script_directory = os.path.dirname(os.path.abspath(__file__))
    json_file        = os.path.join(script_directory, 'amocrmsheets-3d5c4cc53e73.json')
    gh               = GSheets(json_file, file_url=settings.GOOGLEDOCSURL)
    gh.add_df_to_sheets(df=df, sheetname='Лист1')

    answers          = Answer.objects.all().filter(respondentId=profile.external_id)
    answers.delete()
