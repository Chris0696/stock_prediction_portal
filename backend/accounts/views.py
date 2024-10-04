from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .serializers import UserSerializer, UpdateUserSerializer, CreateUserSerializer
from rest_framework import generics
from .models import User
from rest_framework.permissions import AllowAny


class ActivityChoicesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        ACTIVITY_CHOICES = [
            {'value': '1', 'label': 'Trader'},
            {'value': '2', 'label': 'Investor'},
        ]
        return Response(ACTIVITY_CHOICES, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)



class UdapteUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
