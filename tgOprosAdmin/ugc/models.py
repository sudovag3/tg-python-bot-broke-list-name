from django.db import models

class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Id пользователя',
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
    )

    numQuestionProfile = models.PositiveIntegerField(
        verbose_name='Номер вопроса Пользователя',
        default=1,
    )

    typeOfProfile = models.TextField(
        verbose_name='Состояние профиля',
        default='Не определился',
    )

    changedOfProfile = models.TextField(
        verbose_name='Изменяет',
        default='Нет',
    )
    changedThatOfProfile = models.TextField(
        verbose_name='что',
        default='Нет',
    )
    changedThatIdOfProfile = models.TextField(
        verbose_name='Id Заявки',
        default='Нет',
    )
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'#{self.external_id} {self.name} {self.numQuestionProfile} {self.typeOfProfile}'


class Pairs(models.Model):
    pair = models.TextField(verbose_name='Валютная пара')

    def __str__(self):
        return f'#{self.pair}'


class Quotes(models.Model):
    pair = models.ForeignKey(to= Pairs, on_delete=models.CASCADE, verbose_name='Пара')
    quote = models.CharField(verbose_name='Котировка', max_length = 100)
    is_full = models.BooleanField(verbose_name='Требует дописывания?')
    def __str__(self):
        return f'#{self.pair.pair} {self.quote}'

class Register(models.Model):
    сurrency_pair = models.TextField(verbose_name='Валютная пара', null= True, blank=True)
    sum_open = models.CharField(max_length = 100,verbose_name='Цена открытия', null= True, blank=True)
    take_profit = models.TextField(verbose_name='Тейк-профит', null= True, blank=True)
    stop_loss = models.TextField(verbose_name='Стоп-лосс', null= True, blank=True)



    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

class GlobalNum(models.Model):
    num = models.PositiveIntegerField(verbose_name='глобальный счетчик')
    gnum = models.PositiveIntegerField(verbose_name='#', default=1)
    def __str__(self):
        return f'#{self.num} {self.gnum}'

    class Meta:
        verbose_name = 'Счетчик'