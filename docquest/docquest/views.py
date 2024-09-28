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

    agency_address_data = request.data.get('agencyAddress', {})
    project_address_data = request.data.get('projectAddress', {})
    agency_data = request.data.get('agency', {})
    project_data = request.data.get('project', {})
    proponents_data = request.data.get('proponents', {})

    # Extract lists for multiple entries
    goals_and_objectives_list = request.data.get('goalsAndObjectives', [])
    project_activities_list = request.data.get('projectActivities', [])
    budget_requirements_list = request.data.get('budgetRequirements', [])
    eval_and_monitoring_list = request.data.get('evalAndMonitoring', [])
    monitoring_plan_and_schedule_list = request.data.get('monitoringPlanAndSchedule', [])
    target_group_list = request.data.get('targetGroup', [])
    loading_of_trainers_list = request.data.get('loadingOfTrainers', [])
    signatories_list = request.data.get('signatories', [])

    # Create or update the Agency Address
    agency_address_serializer = AddressSerializer(data=agency_address_data)
    if agency_address_serializer.is_valid():
        agency_address = agency_address_serializer.save()
    else:
        return Response(agency_address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create or update the Project Address
    project_address_serializer = AddressSerializer(data=project_address_data)
    if project_address_serializer.is_valid():
        project_address = project_address_serializer.save()
    else:
        return Response(project_address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create or update the Agency
    agency_serializer = PartnerAgencySerializer(data={**agency_data, 'addressID': agency_address.addressID})
    if agency_serializer.is_valid():
        agency = agency_serializer.save()
    else:
        return Response(agency_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create or update the Project
    project_serializer = ProjectSerializer(data={**project_data, 'projectLocationID': project_address.addressID, 'agencyID': agency.agencyID})
    if project_serializer.is_valid():
        project = project_serializer.save()
    else:
        return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create Proponents
    # proponents_serializer = ProponentsSerializer(data={**proponents_data, 'projectID': project.projectID})
    # if proponents_serializer.is_valid():
    #     proponent = proponents_serializer.save()
    # else:
    #     return Response(proponents_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create multiple Goals and Objectives
    for data in goals_and_objectives_list:
        data['projectID'] = project.projectID
        goals_and_objectives_serializer = GoalsAndObjectivesSerializer(data=data)
        if goals_and_objectives_serializer.is_valid():
            goals_and_objectives_serializer.save()
        else:
            return Response(goals_and_objectives_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create multiple Project Activities
    for data in project_activities_list:
        data['projectID'] = project.projectID
        project_activities_serializer = ProjectActivitiesSerializer(data=data)
        if project_activities_serializer.is_valid():
            project_activities_serializer.save()
        else:
            return Response(project_activities_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create multiple Budget Requirements
    for data in budget_requirements_list:
        data['projectID'] = project.projectID
        budget_requirements_serializer = BudgetaryRequirementsItemsSerializer(data=data)
        if budget_requirements_serializer.is_valid():
            budget_requirements_serializer.save()
        else:
            return Response(budget_requirements_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create multiple Eval and Monitoring entries
    for data in eval_and_monitoring_list:
        data['projectID'] = project.projectID
        eval_and_monitoring_serializer = EvaluationAndMonitoringSerializer(data=data)
        if eval_and_monitoring_serializer.is_valid():
            eval_and_monitoring_serializer.save()
        else:
            return Response(eval_and_monitoring_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create multiple Monitoring Plan and Schedule entries
    for data in monitoring_plan_and_schedule_list:
        data['projectID'] = project.projectID
        monitoring_plan_and_schedule_serializer = MonitoringPlanAndScheduleSerializer(data=data)
        if monitoring_plan_and_schedule_serializer.is_valid():
            monitoring_plan_and_schedule_serializer.save()
        else:
            return Response(monitoring_plan_and_schedule_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create multiple target group
    for data in target_group_list:
        data['projectID'] = project.projectID
        target_group_serializer = TargetGroupSerializer(data=data)
        if target_group_serializer.is_valid():
            target_group_serializer.save()
        else:
             return Response(target_group_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create multiple Loading of Trainers entries
    for data in loading_of_trainers_list:
        data['projectID'] = project.projectID
        loading_of_trainers_serializer = LoadingOfTrainersSerializer(data=data)
        if loading_of_trainers_serializer.is_valid():
            loading_of_trainers_serializer.save()
        else:
            return Response(loading_of_trainers_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create multiple Signatories
    for data in signatories_list:
        data['projectID'] = project.projectID
        signatories_serializer = SignatoriesSerializer(data=data)
        if signatories_serializer.is_valid():
            signatories_serializer.save()
        else:
            return Response(signatories_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Project and related data created successfully."}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))