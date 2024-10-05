from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'activity', 'password']

    
    

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'activity', 'password']
        extra_kwargs = {
            'password': {'required': True}
        }

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User with this email id already exists.')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    # def create(self, validated_data):
    #     #  User.objects.create = save the password in a plain text
    #     #  User.objects.create_user = automatically hash password
    #     user = User.objects.create_user(
    #         validated_data['username'],
    #         validated_data['email'],
    #         validated_data['password'],
    #     )
    #     #  User.objects.create_user(**validated_data)
    #     return user
    

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'activity', 'password')

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        if password:
            instance.set_password(password)
        instance = super().update(instance, validated_data)
        return instance