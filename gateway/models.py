from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.
class Gateway_el(models.Model):
    title = models.CharField(null=False,max_length=64,default='',  verbose_name="Название элемента")
    short_description = models.TextField(null=False, default='', verbose_name="Описание карточки")
    status = models.BooleanField(null=False, default=True,  verbose_name="Статус")
    img_url = models.URLField(null=False, default='', verbose_name="Изображение элемента")
    full_description = models.TextField(null=True,blank=True,  verbose_name="Полное описание элемента")
    class Meta:
        verbose_name = "элемент"
        verbose_name_plural = "элементы"
        db_table = 'gateway_el'
class Gateway_mission(models.Model):
    STATUS_CHOICES = (
        (1, 'Введена'),
        (2, 'В работе'),
        (3, 'Завершена'),
        (4, 'Отклонена'),
        (5, 'Удалена'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Cтатус")
    create_datetime = models.DateTimeField(default=timezone.now,verbose_name="Дата создания")
    creator = models.ForeignKey('AuthUser',null=True, default=1, on_delete=models.PROTECT,verbose_name="Пользователь",related_name='creator')
    form_datetime = models.DateTimeField(null=True)
    complete_datetime = models.DateTimeField(null=True)
    moderator = models.ForeignKey('AuthUser',on_delete=models.DO_NOTHING,null=True,verbose_name="Модер", related_name='moder')
    mission_name = models.CharField(null=True, blank=True, verbose_name='Название миссии')
    plan_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата полета')
    addition = models.CharField(null=True, blank=True,verbose_name='Комментарий')
    elements = models.ManyToManyField(Gateway_el, through='gateway_element_and_mission', related_name='missions')
    def get_elements(self):
        return [
            setattr(item.element,"id",item.id) or item.element
            for item in gateway_element_and_mission.objects.filter(mission=self)
        ]
    class Meta:
        verbose_name = "Миссия"
        verbose_name_plural = "Миссии"
        ordering = ('-create_datetime',)
        db_table = 'gateway_missions'


class gateway_element_and_mission(models.Model):

    id = models.AutoField(primary_key=True, serialize=True)
    mission = models.ForeignKey(Gateway_mission,on_delete=models.DO_NOTHING,related_name='m_id')
    element = models.ForeignKey(Gateway_el,on_delete=models.DO_NOTHING,related_name='el_id')
    addition = models.CharField(max_length=256, blank=True, null=True, verbose_name="Комментарий")
    class Meta:
        verbose_name = 'м-м'
        verbose_name_plural = verbose_name
        db_table = 'gateway_element_and_mission'
        constraints = [
            models.UniqueConstraint(fields=['mission','element'],name="mission_el_constraint")
        ]


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    class Meta:
        managed = False
        db_table = 'auth_user'
