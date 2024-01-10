from django.http import HttpResponse
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import User

class HelloWorldView(APIView):

    def get(self, request):
        print(request.user)
        return HttpResponse("Hello, World!")
