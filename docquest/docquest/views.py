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
    # Fetch user by email
    user = get_object_or_404(User, email=request.data['email'])

    # Check password
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create token for the user
    token, created = Token.objects.get_or_create(user=user)

    # Serialize user data
    user_serializer = UserSerializer(instance=user)

    # Fetch and serialize user's roles
    roles = user.role.all()  # Get all roles associated with the user
    role_serializer = RoleSerializer(roles, many=True)  # Serialize the roles

    # Return combined response with user data and roles
    return Response({
        "token": token.key,
        "user": user_serializer.data,
        "roles": role_serializer.data
    })

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)

        # Assign user's role
        role_data = {
            "userID": user.userID,  # Set userID to the new user's ID
            "role": request.data.get("role"),
        }

        role_serializer = RoleSerializer(data=role_data)
        if role_serializer.is_valid():
            role_serializer.save()
            return Response({"token": token.key, "user": serializer.data,
                            "message": "User created and role assigned",
                            }, status=status.HTTP_201_CREATED)
        else:
            return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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