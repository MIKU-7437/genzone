from .models import Conversation, Message
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User
from .serializers import ConversationListSerializer, ConversationSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, reverse
from rest_framework import status

@api_view(['POST'])
def start_convo(request):
    email = request.data.get('email')
    participant = get_object_or_404(User, email=email)
    
    conversation = Conversation.objects.filter(Q(initiator=request.user, receiver=participant) |
                                               Q(initiator=participant, receiver=request.user)).first()

    if conversation:
        return redirect(reverse('get_conversation', args=(conversation.id,)))
    else:
        conversation = Conversation.objects.create(initiator=request.user, receiver=participant)
        serializer = ConversationSerializer(instance=conversation, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_conversation(request, convo_id):
    conversation = get_object_or_404(Conversation, id=convo_id)
    serializer = ConversationSerializer(instance=conversation, context={"request": request})
    return Response(serializer.data)

@api_view(['GET'])
def conversations(request):
    conversation_list = Conversation.objects.filter(Q(initiator=request.user) |
                                                    Q(receiver=request.user))
    serializer = ConversationListSerializer(instance=conversation_list, many=True, context={"request": request})
    return Response(serializer.data)
