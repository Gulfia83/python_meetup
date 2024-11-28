from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Letters, User, Program, Application

@receiver(post_save, sender=Letters)
def send_newsletter_on_save(sender, instance, created, **kwargs):
    if created and instance.sent_at is None:
        instance.send_to_all_users()


@receiver(post_save, sender=User)
def handle_active_update(sender, instance, created, update_fields, **kwargs):
    if not created and update_fields and "active" in update_fields:
        instance.send_about_new_user()


@receiver(post_save, sender=Program)
def send_new_progrum(sender, instance, created, **kwargs):
    if created:
        instance.send_program()


@receiver(post_save, sender=Application)
def send_notification_on_application_accepted(sender, instance, created, **kwargs):
    if not created and instance.accepted:
        user = instance.applicant.tg_id
        instance.send_accept(user)
