from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, reverse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import jwt
from .models import User
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .utils import Util


class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        RegisterView (Регистрация нового пользователя):

        Описание: Регистрирует нового пользователя в системе и отправляет электронное письмо для подтверждения адреса электронной почты.
        Параметры:
        first_name (обязательный): Имя пользователя.
        last_name (обязательный): Фамилия пользователя.
        email (обязательный): Адрес электронной почты пользователя.
        password (обязательный): Пароль пользователя.
        password_conf (обязательный): Подтверждение пароля пользователя.
        Ответ:
        user_data: Данные пользователя.
        """
        password = request.data.get('password')
        password_conf = request.data.get('password_conf')

        # Проверка соответствия паролей
        if password != password_conf:
            return Response({'error': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)

        # Создание экземпляра сериализатора
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.data

        # Получение токенов доступа
        user_email = User.objects.get(email=user['email'])
        token = RefreshToken.for_user(user_email).access_token

        # Формирование URL для верификации по электронной почте
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        verify_url = 'http://' + current_site + relative_link + "?token=" + str(token)

        # текста электронного письма
        email_body = f"Привет {user['email']}, активируй свой аккаунт.\n{verify_url}"

        # Подготовка данных и отправка электронного письма
        data = {
            'email_body': email_body,
            'to_email': user['email'],
            'email_subject': 'Verify your email'
        }
        Util.send_email(data=data)

        # Возврат ответа с данными пользователя и токеном доступа
        return Response({'user_data': user}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], name='check_status')
    def check_status(self, request):
        """
        Описание: Проверяет статус подтверждения адреса электронной почты для указанного пользователя.
        Параметры:
        email (обязательный): Адрес электронной почты пользователя.
        Ответ:
        status: Статус подтверждения (verified - подтверждено, error - не подтверждено).
        """
        email = request.data.get('email')
        user = User.objects.get(email=email)
        if user:
            if user.is_active:
                return Response({'status': "активирован"})
            else:
                return Response({'error': f"Пользователь с почтой {email} еще не активирован"})
        else:
            return Response({'error': f"Пользователя с почтой {email} не существует"})

    # Функция для повторной отправки токена, если истечет время
    @action(detail=False, methods=['post'], name='get_another_mail')
    def getAnotherMail(self, request):
        """
        Метод: POST
        Описание: Повторно отправляет токен подтверждения адреса электронной почты для указанного пользователя.
        Параметры:
        email (обязательный): Адрес электронной почты пользователя.
        Ответ:
        email: Адрес электронной почты пользователя.
        """
        try:
            # Проверка корректности и наличия email в базе данных
            email = request.data.get('email')
            if not email:
                raise ValidationError({'email': 'Email is required'})

            user = User.objects.get(email=email)

            # Создание токена доступа
            token = RefreshToken.for_user(user).access_token

            # Формирование URL для верификации по электронной почте
            current_site = get_current_site(request).domain
            relative_link = reverse('email-verify')
            verify_url = 'http://' + current_site + relative_link + "?token=" + str(token)

            # Формирование текста электронного письма
            email_body = f"Hi {user.username}, verify your email.\n{verify_url}"

            # Подготовка данных и отправка электронного письма
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Verify your email'
            }
            Util.send_email(data=data)

            # Возврат ответа с адресом электронной почты пользователя и токеном доступа
            return Response({'email': user.email}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        """
        Описание: Подтверждает адрес электронной почты пользователя по токену, отправленному на почту.
        Параметры:
        token (в параметрах запроса): Токен подтверждения.
        Ответ:
        email: Статус успешного подтверждения.
        """
        # Получение токена из параметра запроса
        token = request.GET.get('token')

        try:
            # Декодирование токена 
            token_data = jwt.decode(token, options={
                "verify_signature": False})  # ("verify_signature": False)не обращать внимание

            # Получение пользователя по ID из токена и поиск пользователя с таким id
            user = User.objects.get(id=token_data['user_id'])

            # Проверка, что пользователь не подтвержден, и если так, подтверждение
            if not user.is_active:
                user.is_active = True
                user.save()

            return Response({'email': 'Успешно активирован'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            # Истекший токен
            return Response({'error': 'Срок действия активации истек, попробуйте снова'},
                            status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            # Невозможности декодирования токена
            return Response({'error': 'Нерабочий токен'}, status=status.HTTP_400_BAD_REQUEST)


# перезапись функции ради добавления контекста(рендер абсолютного URL)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data, context={"request": request})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# Testing logic
class UserDetailView(APIView):
    permission_classes = [IsOwnerOrReadOnly,]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)
        return user

    def get(self, request, pk):
        """
        Логика для работы с аккаунтом:

        Описание: Получает данные аутентифицированного пользователя.
        для работы с эндпоинтом, нужно предоставить access токен
        Ответ: Данные пользователя

        """
        user = self.get_object()
        # Сериализация и возврат данных пользователя, передаем запрос в контексте для создания абсолютного url
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)

    # Функция, которая будет срабатывать только на PUT-запросы(обновить данные и пользователе)
    def put(self, request, pk):
        """
        Описание: Обновляет данные аутентифицированного пользователя.
        Параметры которые можно редактировать:
        first_name (необязательный): Новое имя пользователя.
        last_name (необязательный): Новая фамилия пользователя.
        photo (необязательный): Новая фотография пользователя.
        username: полное имя пользователя, состоит из first_name и last_name
        Ответ: Обновленные данные пользователя.
        """
        user = self.get_object()
        self.check_object_permissions(self.request, user)

        serializer = UserSerializer(user, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # TESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTEST
    def delete(self, request, pk, format=None):
        """
        Описание: Удаляет аутентифицированного пользователя.
        Ответ: Сообщение об успешном удалении.z
        """
        # Получение объекта пользователя
        user = self.get_object()

        # Удаление пользователя
        email = user.email
        user.delete()
        return Response({'message': f'User with email {email} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# TESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTEST
class AllUsersView(APIView):
    """
    Описание: (Тестовая функция) 
    Получает данные всех пользователей в системе.
    Ответ: Данные всех пользователей.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Получение всех пользователей
        users = User.objects.all()

        # Сериализация и возврат данных всех пользователей
        serializer = UserSerializer(users, context={"request": request}, many=True)
        return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Метод: PUT
    Описание: Изменяет пароль пользователя.
    Параметры:
    old_password (обязательный): Текущий пароль пользователя.
    new_password (обязательный): Новый пароль пользователя.
    Ответ: Сообщение об успешном обновлении пароля.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Проверка старого пароля
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # хеширование нового пароля
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
