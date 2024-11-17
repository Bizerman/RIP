from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.
class Gateway_el(models.Model):
    title = models.CharField(null=True,blank=True,max_length=64)
    short_description = models.TextField(null=True,blank=True)
    status = models.BooleanField(null=True, blank=True,default=True)
    img_url = models.URLField(null=True, blank=True)
    full_description = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = "элемент"
        verbose_name_plural = "элементы"
        db_table = 'gateway_el'
class Gateway_mission(models.Model):
    STATUS_CHOICES = (
        (1,'Введен'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален'),
    )
    status = models.CharField(choices=STATUS_CHOICES,default=1,verbose_name="Cтатус")
    create_datetime = models.DateTimeField(default=timezone.now,verbose_name="Дата создания")
    creator = models.ForeignKey(User,null=True,default=2,on_delete=models.PROTECT,verbose_name="Пользователь",related_name='creator')
    form_datetime = models.DateTimeField(null=True)
    complete_datetime = models.DateTimeField(null=True)
    moderator = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,verbose_name="Модер", related_name='moder')
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
    id = models.AutoField(primary_key=True,serialize=True)
    mission = models.ForeignKey(Gateway_mission,on_delete=models.DO_NOTHING,related_name='m_id')
    element = models.ForeignKey(Gateway_el,on_delete=models.DO_NOTHING,related_name='el_id')
    class Meta:
        verbose_name = 'м-м'
        verbose_name_plural = verbose_name
        db_table = 'gateway_element_and_mission'
        constraints = [
            models.UniqueConstraint(fields=['mission','element'],name="mission_el_constraint")
        ]