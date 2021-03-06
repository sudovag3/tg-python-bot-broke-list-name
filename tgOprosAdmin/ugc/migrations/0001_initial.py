# Generated by Django 3.1.1 on 2020-09-29 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respondentId', models.PositiveIntegerField(verbose_name='Id ответчика')),
                ('numAnswer', models.PositiveIntegerField(verbose_name='Номер ответа')),
                ('onWhatQuestion', models.TextField(verbose_name='На какой вопрос')),
                ('textAnswer', models.TextField(verbose_name='Содержимое ответа')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(verbose_name='Id пользователя')),
                ('name', models.TextField(verbose_name='Имя пользователя')),
                ('numQuestionProfile', models.PositiveIntegerField(default=1, verbose_name='Номер вопроса Пользователя')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numQuestion', models.PositiveIntegerField(verbose_name='Номер вопроса')),
                ('question', models.TextField(verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
    ]
