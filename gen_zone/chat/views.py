# views.py
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, reverse
from rest_framework import status
from django.db.models import Q
from .models import Conversation, Message
from users.models import User
from .serializers import ConversationListSerializer, ConversationSerializer, MessageSerializer, CustomPageNumberPagination



# Представление для начала нового разговора или перенаправления на существующий
class StartConvoView(CreateAPIView):
    """
    начало нового диалога или перенаправления к существующему.

    Параметры:
    - email: Электронная почта участника разговора.

    Возвращает:
    - 201 Created: Если новый разговор начат успешно.
    - Redirect: Если найден существующий разговор, перенаправляет на него.

    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        participant = get_object_or_404(User, email=email)

        conversation = Conversation.objects.filter(Q(initiator=request.user, receiver=participant) |
                                                   Q(initiator=participant, receiver=request.user)).first()

        if conversation:
            return Response(ConversationSerializer(instance=conversation, context={"request": request}).data,
                            status=status.HTTP_302_FOUND)
        else:
            conversation = Conversation.objects.create(initiator=request.user, receiver=participant)
            serializer = ConversationSerializer(instance=conversation, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# Представление для получения разговора по его идентификатору
class GetConversationView(RetrieveAPIView):
    """
    получение диалога по его айди с пагинацией(обычно по 10).

    Параметры:
    - pk: Идентификатор разговора.

    Возвращает:
    - 200 OK: Возвращает детали разговора с пагинированными сообщениями.
    P.S.
    времено оставил message_set(возвращает все сообщения)
    для изменения количества сообщений нужно добавить "?page_size=num"(максимум 100)
    "http://127.0.0.1:8000/api/conversations/1/?page_size=20"
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.all()
    pagination_class = CustomPageNumberPagination  # Используйте ваш класс пагинации

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Получаем все сообщения
        messages = Message.objects.filter(conversation_id=instance.id).order_by('-timestamp')

        # Пагинируем сообщения, используя указанный класс пагинации
        paginated_messages = self.paginate_queryset(messages)

        # Сериализуем разговор с пагинированными сообщениями
        serializer = self.get_serializer(instance)
        serialized_data = serializer.data
        serialized_data['messages'] = MessageSerializer(instance=paginated_messages, many=True).data

        return self.get_paginated_response(serialized_data)


# Представление для получения списка разговоров пользователя
class ConversationsListView(ListAPIView):
    """
    получение списка разговоров пользователя.

    Возвращает:
    - 200 OK: Возвращает список разговоров пользователя.

    """
    serializer_class = ConversationListSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(initiator=user) | Q(receiver=user))