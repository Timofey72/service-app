from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Subscription, Service, Plan
from .tasks import set_price


@receiver(pre_save, sender=Service)
def pre_save_service(sender, instance, **kwargs):
    old_full_price = sender.objects.filter(pk=instance.pk).values_list('full_price', flat=True).first()
    if old_full_price != instance.full_price:
        for subscription_id in list(instance.subscriptions.all().values_list('id', flat=True)):
            def start_task_for_subscription(sub_id: int):
                transaction.on_commit(lambda: set_price.delay(sub_id))

            start_task_for_subscription(subscription_id)


@receiver(pre_save, sender=Plan)
def pre_save_plan(sender, instance, **kwargs):
    old_discount_percent = sender.objects.filter(pk=instance.pk).values_list('discount_percent', flat=True).first()
    if old_discount_percent != instance.discount_percent:
        for subscription_id in list(instance.subscriptions.all().values_list('id', flat=True)):
            def start_task_for_subscription(sub_id: int):
                transaction.on_commit(lambda: set_price.delay(sub_id))

            start_task_for_subscription(subscription_id)


@receiver(pre_save, sender=Subscription)
def pre_save_subscription(sender, instance, **kwargs):
    old_plan = sender.objects.filter(pk=instance.pk).values_list('plan', flat=True).first()
    if old_plan != instance.plan.id:
        transaction.on_commit(lambda: set_price.delay(instance.pk))
