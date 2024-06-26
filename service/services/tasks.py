import datetime

from celery import shared_task
from celery_singleton import Singleton

from django.conf import settings
from django.core.cache import cache

from django.db import transaction
from django.db.models import F


@shared_task(base=Singleton)
def set_price(subscription_id: int):
    from .models import Subscription

    with transaction.atomic():
        subscription = Subscription.objects.select_for_update().filter(id=subscription_id).annotate(
            annotated_price=F('service__full_price') - (F('service__full_price')
                                                        * F('plan__discount_percent')) / 100).first()

        subscription.price = subscription.annotated_price
        subscription.save()

    cache.delete(settings.PRICE_CACHE_NAME)


@shared_task(base=Singleton)
def set_comment(subscription_id: int):
    from .models import Subscription

    with transaction.atomic():
        subscription = Subscription.objects.select_for_update().get(id=subscription_id)

        subscription.comment = f'Update time: {datetime.datetime.now()}'
        subscription.save()

    cache.delete(settings.PRICE_CACHE_NAME)


def start_task_for_subscription(sub_id: int):
    transaction.on_commit(lambda: set_price.delay(sub_id))
    transaction.on_commit(lambda: set_comment.delay(sub_id))
