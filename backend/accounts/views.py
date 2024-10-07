from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .serializers import UserSerializer, UpdateUserSerializer, CreateUserSerializer, LoginSerializer, CustomTokenObtainPairSerializer
from rest_framework import generics
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from rest_framework_simplejwt.views import TokenObtainPairView



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)



class UdapteUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer



class LoginAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        # Initialize serializer with query data
        serializer = self.serializer_class(data=request.data)

        # Validate serializer data
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Return tokens and user information
            return Response({
                'refresh': str(refresh),
                'access': str(access_token),
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivityChoicesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        ACTIVITY_CHOICES = [
            {'value': '1', 'label': 'Trader'},
            {'value': '2', 'label': 'Investor'},
        ]
        return Response(ACTIVITY_CHOICES, status=status.HTTP_200_OK)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = {
            'status': 'Request was permitted'
        }
        return Response(response)










