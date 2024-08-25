from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def roles(request):
    # Retrieve the userID from the request data
    user_id = request.data.get('userID')

    # Manually check if userID exists in CustomUser
    if not User.objects.filter(userID=user_id).exists():
        return Response("User does not exist.", status=status.HTTP_400_BAD_REQUEST)
    
    # Check if the user already has a role entry in the Roles table
    try:
        role_instance = Roles.objects.get(userID=user_id)
    except Roles.DoesNotExist:
        role_instance = None
    
    # Initialize the serializer with the instance to update if it exists
    serializer = RoleSerializer(instance=role_instance, data=request.data)
    
    if serializer.is_valid():
        serializer.save()  # Save will either create a new instance or update the existing one
        return Response("Successfully assigned/updated role/s.", status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))