from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view({'post': 'post'}), name='register'),
    path('email-verify/', views.VerifyEmailView.as_view(), name='email-verify'),
    path('check_status/', views.RegisterView.as_view({'post': 'check_status'}), name='check_status'),
    path('another-mail/', views.RegisterView.as_view({'post': 'getAnotherMail'}), name='get-another-mail'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', views.AllUsersView.as_view(), name='account-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='account-detail'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]