from django.contrib.auth.models import User
from django.db.models import Prefetch
from rest_framework import mixins
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Client
from .serializers import ClientSerializer


class ClientView(ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Client.objects.all().prefetch_related(
        Prefetch('user', queryset=User.objects.all().only('id', 'username', 'email'))
    )
    serializer_class = ClientSerializer
