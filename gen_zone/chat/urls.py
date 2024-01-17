from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.StartConvoView.as_view(), name='start_convo'),
    path('<int:pk>/', views.GetConversationView.as_view(), name='get_conversation'),
    path('', views.ConversationsListView.as_view(), name='conversations')
]
