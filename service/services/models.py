from django.db import models
from django.core.validators import MaxValueValidator

from clients.models import Client


class Service(models.Model):
    name = models.CharField(max_length=64)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f'Service: {self.name} = {self.full_price} р.'


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return f'Plan: {self.plan_type} ({self.discount_percent}%)'


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=64, default='', db_index=True)

    def __str__(self):
        return f'{self.client}; {self.service}'
