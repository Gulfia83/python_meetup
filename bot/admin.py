from django.contrib import admin

from .models import Donate, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "name", "company", "position", "status")


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "donated_at",
    )
