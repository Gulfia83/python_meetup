from django.db import models
from django.utils import timezone
from python_meetup.settings import TG_BOT_TOKEN
from telegram import Bot


class User(models.Model):
    tg_id = models.CharField(
        "телеграм id",
        max_length=50,
        blank=True,
        unique=True,
        db_index=True,
    )
    tg_nick = models.CharField(
        'Ник в телеграм',
        max_length=50,
        blank=True,
    )
    tg_state = models.CharField(
        'Состояние бота',
        max_length=50,
        default='START'
    )
    name = models.CharField(
        "Имя",
        max_length=50,
        blank=True,
        null=True,
    )
    company = models.CharField(
        "Компания",
        max_length=100,
        blank=True,
        null=True,
    )
    position = models.CharField(
        "Должность",
        max_length=100,
        blank=True,
        null=True,
    )
    STATUS_CHOICES = [
        ("PARTICIPANT", "Участник"),
        ("SPEAKER", "Спикер"),
        ("MANAGER", "Менеджер"),
    ]
    status = models.CharField(
        "Статус", max_length=50, choices=STATUS_CHOICES, default="PARTICIPANT"
    )
    active = models.BooleanField(
        'Готов/не готов к общению',
        default=False
    )
    ready_to_questions = models.BooleanField(
        'Готов/не готов получать вопросы',
        default=False
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.tg_id}"

    class Meta:
        verbose_name = ("Участник",)
        verbose_name_plural = "Участники"


    def send_about_new_user(self):
        bot = Bot(token=TG_BOT_TOKEN)
        users = User.objects.filter(active=True).count()
        if users == 2:
            users_active = User.objects.filter(ready_to_questions=True)
            for user in users_active:
                try:
                    bot.send_message(chat_id=user.tg_id, text="Новый пользователь зарегистрировался! Теперь вы можете пообщаться.")
                except Exception as e:
                    print(f"Ошибка при отправке сообщения пользователю {user.tg_id}: {e}")


class Lecture(models.Model):
    name = models.CharField("Название лекции", max_length=255)
    description = models.TextField("Описание лекции")
    start_time = models.DateTimeField("Начало лекции")
    end_time = models.DateTimeField("Конец лекции")
    speaker = models.ForeignKey(
        User,
        related_name="lecture",
        on_delete=models.DO_NOTHING,
        verbose_name="Докладчик",
    )
    STATUS_CHOICES = [
        ("PLANNED", "Запланирована"),
        ("ONGOING", "Идёт"),
        ("COMPLETED", "Завершена"),
    ]
    status = models.CharField(
        "Статус лекции", max_length=20, choices=STATUS_CHOICES, default="PLANNED"
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.speaker}"

    class Meta:
        verbose_name = "Доклад"
        verbose_name_plural = "Доклады"
        ordering = ["start_time"]


class Program(models.Model):
    name = models.CharField("Название программы", max_length=255)
    lectures = models.ManyToManyField(
        Lecture, related_name="programs", verbose_name="Лекции"
    )
    date = models.DateField("Дата проведения программы", blank=True, null=True)

    def __str__(self) -> str:
        return f"Программа - {self.name}"

    class Meta:
        verbose_name = "Программа"
        verbose_name_plural = "Программы"


class Donate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Кто задонатил",
        related_name="donates",
    )
    amount = models.DecimalField("Сумма", decimal_places=2, max_digits=8, default=0)
    donated_at = models.DateTimeField(
        "Время доната",
        default=timezone.now(),
    )

    def __str__(self) -> str:
        return f"{self.user.name} - {self.amount}"

    class Meta:
        verbose_name = ("Донат",)
        verbose_name_plural = "Донаты"


class Questions(models.Model):
    asker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="От кого",
        related_name="questions_from"
    )
    answerer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Кому",
        related_name="questions_to",
    )
    text = models.TextField(
        "Текст вопроса",
        blank=True,
    )
    asked_at = models.DateTimeField(
        "Время создания",
        default=timezone.now()
    )

    def __str__(self) -> str:
        return f"Вопрос {self.answerer.__str__()}"

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Letters(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Рассылка",)
        verbose_name_plural = "Рассылки"

    def send_to_all_users(self):
        bot = Bot(token=TG_BOT_TOKEN)

        users = User.objects.all()

        for user in users:
            try:
                bot.send_message(chat_id=user.tg_id, text=self.message)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user.tg_id}: {e}")

        self.sent_at = timezone.now()
        self.save()
