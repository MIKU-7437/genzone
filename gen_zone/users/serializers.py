from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username','first_name', 'last_name', 'email', 'role', 'photo', 'courses', 'courses_owned', 'courses_favorite')
        read_only_fields = ('email', 'username','role')

    # redacting 'username' field depending on 'first_name' and 'last_name'
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        instance.username = f"{instance.first_name} {instance.last_name}"

        serializer = UserSerializer(instance, data=validated_data)
        return super().update(instance, validated_data)
    # return absolute_url for photo example:http://127.0.0.1:8000/media/customer_photos/default-profile-picture.jpg
    def get_photo_url(self, user):
        request = self.context.get('request')
        photo_url = user.photo.url
        return request.build_absolute_uri(photo_url)


class RegisterSerializer(serializers.ModelSerializer):
    password_conf = serializers.CharField(write_only=True)  # Поле для подтверждения пароля

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'password_conf')

    # def validate(self, data):
    #     # Проверяем, совпадают ли пароли
    #     if 'password' in data and 'password_conf' in data:
    #         if data['password'] != data['password_conf']:
    #             raise serializers.ValidationError("Пароли не совпадают.")
    #     return data

    def create(self, validated_data):
        # Удаляем поле 'password_conf' из validated_data перед созданием пользователя
        password_conf = validated_data.pop('password_conf', None)
        
        # Создаем пользователя с использованием метода create_user вашей модели User
        user = User.objects.create_user(**validated_data)

        # Устанавливаем пароль для пользователя
        user.set_password(validated_data['password'])

        user.username = f"{user.first_name} {user.last_name}"
        user.save()

        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    # Сериализатор для подтверждения электронной почты

    # Добавление поля для токена
    token = serializers.CharField(max_length=600)

    class Meta:
        model = User
        # Поля, которые будут включены в сериализацию
        fields = ['token']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Include additional user data in the response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            "username": self.user.username,
            'role': self.user.role,
            'photo': self.get_photo_url(self.user),
        }

        return data
    # return absolute_url for photo example:http://127.0.0.1:8000/media/customer_photos/default-profile-picture.jpg
    def get_photo_url(self, user):
        request = self.context.get('request')
        photo_url = user.photo.url
        return request.build_absolute_uri(photo_url)

class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
