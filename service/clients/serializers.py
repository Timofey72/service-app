from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Client


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Client
        fields = ('id', 'company_name', 'full_address', 'user')

    def create(self, validated_data):
        username = validated_data['user'].get('username', '')
        email = validated_data['user'].get('email', '')
        return Client.objects.create(company_name=validated_data['company_name'],
                                     full_address=validated_data['full_address'],
                                     user=User.objects.create(username=username, email=email))
