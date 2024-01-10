from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'initiator', 'receiver', 'start_time')
    list_filter = ('initiator', 'receiver', 'start_time')
    search_fields = ('initiator__username', 'receiver__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'text', 'conversation_id', 'timestamp')
    list_filter = ('sender', 'conversation_id', 'timestamp')
    search_fields = ('sender__username', 'text', 'conversation_id__id')
