from rest_framework import serializers

from companies.serializers import CompanySerializer
from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'name', 'company_id', 'password', 'email']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            name=validated_data['name'],
            company_id=validated_data['company_id'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserListRetrieveSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = User
        fields = ['username', 'name', 'company', 'email']
