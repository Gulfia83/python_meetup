from django.db import models
from django.utils import timezone


class User(models.Model):
    tg_id = models.CharField(
        'телеграм id',
        max_length=50,
        blank=True,
    )
    tg_state = models.CharField(
        'Состояние бота',
        max_length=50,
        default='START'
    )
    name = models.CharField(
        'Имя',
        max_length=50,
        blank=True
    )
    company = models.CharField(
        'Компания',
        max_length=100,
        blank=True
    )
    position = models.CharField(
        'Должность',
        max_length=100,
        blank=True
    )
    STATUS_CHOICES = [
        ('PARTICIPANT', 'Участник'),
        ('SPEAKER', 'Спикер')
    ]
    status = models.CharField(
        'Статус',
        max_length=50,
        choices=STATUS_CHOICES,
        default='PARTICIPANT'
    )
    active = models.BooleanField(
        'Готов/не готов к общению',
        default=False
    )

    def __str__(self) -> str:
        return f'{self.name} - {self.tg_id}'
  
    class Meta:
        verbose_name = 'Участник',
        verbose_name_plural = 'Участники'


class Donate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кто задонатил',
        related_name='donates'
        )
    amount = models.DecimalField(
        'Сумма',
        decimal_places=2,
        max_digits=8,
        default=0
        )
    donated_at = models.DateTimeField(
        'Время доната',
        default=timezone.now(),
    )

    def __str__(self) -> str:
        return f'{self.user.name} - {self.amount}'

    class Meta:
        verbose_name = 'Донат',
        verbose_name_plural = 'Донаты'
