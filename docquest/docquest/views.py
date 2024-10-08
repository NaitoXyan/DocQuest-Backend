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
from rest_framework.permissions import IsAuthenticated, AllowAny

User = get_user_model()

# signup
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()

        return Response({"message": "User created and role assigned",},
                            status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# inig login mag fetch user name and roles
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def name_and_roles(request):
    user = request.user  # Get the authenticated user from the request

    # Serialize user data
    user_serializer = UserLoginSerializer(instance=user)

    # Return combined response with user data and roles
    return Response({
        "userID": user_serializer.data['userID'],
        "firstname": user_serializer.data['firstname'],
        "lastname": user_serializer.data['lastname'],
        "roles": user_serializer.data['roles']
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user  # Get the authenticated user from the request

    # Serialize user data
    user_serializer = UserEditProfileSerializer(instance=user)

    # Return combined response with user data and roles
    return Response(user_serializer.data)

# edit user profile
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_profile(request, pk):
    try:
        instance = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "Object not found."}),

    serializer = UserEditProfileSerializer(instance, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    serializer = PostProjectSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Project successfuly created"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, pk): 
    user = request.user  # Get the authenticated user

    # Try to fetch the project by its ID
    try:
        project = Project.objects.get(pk=pk)  # Use pk to fetch the project directly
    except Project.DoesNotExist:
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    project_serializer = GetProjectSerializer(instance=project)
    return Response(project_serializer.data)

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