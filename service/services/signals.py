from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver

from .models import Subscription, Service, Plan
from .tasks import set_price, set_comment


@receiver(pre_save, sender=Service)
def pre_save_service(sender, instance, **kwargs):
    old_full_price = sender.objects.filter(pk=instance.pk).values_list('full_price', flat=True).first()
    if old_full_price != instance.full_price:
        for subscription_id in list(instance.subscriptions.all().values_list('id', flat=True)):
            def start_task_for_subscription(sub_id: int):
                transaction.on_commit(lambda: set_price.delay(sub_id))
                transaction.on_commit(lambda: set_comment.delay(sub_id))

            start_task_for_subscription(subscription_id)


@receiver(pre_save, sender=Plan)
def pre_save_plan(sender, instance, **kwargs):
    old_discount_percent = sender.objects.filter(pk=instance.pk).values_list('discount_percent', flat=True).first()
    if old_discount_percent != instance.discount_percent:
        for subscription_id in list(instance.subscriptions.all().values_list('id', flat=True)):
            def start_task_for_subscription(sub_id: int):
                transaction.on_commit(lambda: set_price.delay(sub_id))
                transaction.on_commit(lambda: set_comment.delay(sub_id))

            start_task_for_subscription(subscription_id)


@receiver(pre_save, sender=Subscription)
def pre_save_subscription(sender, instance, **kwargs):
    if instance.pk is None:
        return

    old_plan, old_service = sender.objects.filter(pk=instance.pk).values_list('plan', 'service').first()
    if (old_plan != instance.plan.id) or (old_service != instance.service.id):
        def start_task_for_subscription(sub_id: int):
            transaction.on_commit(lambda: set_price.delay(sub_id))
            transaction.on_commit(lambda: set_comment.delay(sub_id))

        start_task_for_subscription(instance.pk)


@receiver(post_save, sender=Subscription)
def post_save_subscription(instance, created, **kwargs):
    if created:
        def start_task_for_subscription(sub_id: int):
            transaction.on_commit(lambda: set_price.delay(sub_id))
            transaction.on_commit(lambda: set_comment.delay(sub_id))

        start_task_for_subscription(instance.pk)


@receiver(post_delete, sender=Subscription)
def post_delete_subscription(sender, instance, **kwargs):
    cache.delete(settings.PRICE_CACHE_NAME)
