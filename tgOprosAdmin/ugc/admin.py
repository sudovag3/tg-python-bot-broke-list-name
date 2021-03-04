from django.contrib import admin

from .models import *


@admin.register(Pairs)
class PairsAdmin(admin.ModelAdmin):
    list_display = ('pair',)

@admin.register(Quotes)
class QuotesAdmin(admin.ModelAdmin):
    list_display = ('pair', 'quote', 'is_full')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name', 'numQuestionProfile', 'typeOfProfile')


# Register your models here.

@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'сurrency_pair', 'sum_open', 'take_profit')

