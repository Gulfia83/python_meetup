from django.contrib import admin
from .models import Donate, Lecture, Program, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "name", "company", "position", "status")


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "start_time",
        "end_time",
        "speaker",
        "status",
    )


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "date")


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "donated_at",
    )
