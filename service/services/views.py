from django.conf import settings
from django.db.models import Prefetch, Sum
from django.core.cache import cache
from rest_framework import mixins
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from clients.models import Client
from .models import Subscription, Plan, Service
from .serializers import SubscriptionSerializer, PlanSerializer, ServiceSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    )
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.PRICE_CACHE_NAME)

        if price_cache:
            total_amount = price_cache
        else:
            total_amount = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_amount, 60 * 60)

        response_data = {'result': response.data, 'total_amount': total_amount}
        response.data = response_data

        return response


class PlanView(ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class ServiceView(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
