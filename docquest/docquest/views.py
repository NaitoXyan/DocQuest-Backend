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

@api_view(['POST'])
def create_project(request):

    address_data = {
        'addressID' : request.data.get('addressID'),
        'street' : request.data.get('street'),
        'barangay' : request.data.get('barangay'),
        'city' : request.data.get('city'),
        'province' : request.data.get('province'),
        'postalCode' : request.data.get('postalCode')
    }

    agency_data = {
        'agencyID': request.data.get('agencyID'),
        'agencyName' : request.data.get('agencyName'),
        'addressID' : request.data.get('addressID')
    }

    project_data = {
        'projectID' : request.data.get('projectID'),
        'programCategory' : request.data.get('programCategory'),
        'projectTitle' : request.data.get('projectTitle'),
        'projectType' : request.data.get('projectType'),
        'projectCategory' : request.data.get('projectCategory'),
        'researchTitle': request.data.get('researchTitle'),
        'program' : request.data.get('program'),
        'accreditationLevel' : request.data.get('accreditationLevel'),
        'college' : request.data.get('college'),
        'projectLocationID': request.data.get('projectLocationID'),
        'agencyID' : request.data.get('agencyID'),
        'targetImplementation' : request.data.get('targetImplementation'),
        'totalHours' : request.data.get('totalHours'),
        'background' : request.data.get('background'),
        'projectComponent' : request.data.get('projectComponent'),
        'beneficiaries' : request.data.get('beneficiaries'),
        'totalBudget' : request.data.get('totalBudget'),
        'moaID' : request.data.get('moaID') #leave it sa?
    }

    target_group_data = {
        'targetGroupID' : request.data.get('targetGroupID'),
        'targetGroup' : request.data.get('targetGroup'),
        'projectID' : request.data.get('projectID')
    }

    goals_and_objectives_data = {
        'GAOID' : request.data.get('GAOID'), 
        'goalsAndObjectives' : request.data.get('goalsAndObjectives'), 
        'projectID' : request.data.get('projectID')
    }

    monitoring_plan_and_schedule_data = {
        'MPASID' : request.data.get('MPASID'), 
        'approach' : request.data.get('approach'), 
        'dataGatheringStrategy' : request.data.get('dataGatheringStrategy'), 
        'schedule' : request.data.get('schedule'), 
        'implementationPhase' : request.data.get('implementationPhase'),
        'projectID' : request.data.get('projectID')
    }

    # project_serializer = ProjectSerializer(data=project_data)
    # if project_serializer.is_valid():

    # return Response()

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))