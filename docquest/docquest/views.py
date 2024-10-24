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
@permission_classes([AllowAny])
def create_role(request):
    role_serializer = RoleSerializer(data=request.data)

    if role_serializer.is_valid():
        role_serializer.save()
        return Response({"message": "Role successfuly created"}, status=status.HTTP_201_CREATED)

    return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    serializer = PostProjectSerializer(data=request.data)

    if serializer.is_valid():
        project = serializer.save()

        if project.dateCreated and not project.uniqueCode:
            project.uniqueCode = f"{project.projectID}-{project.dateCreated.strftime('%Y%m%d')}"
        project.save()

        return Response({"message": "Project successfuly created"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_project(request, pk): 
    user = request.user  # Get the authenticated user

    # Try to fetch the project by its ID
    try:
        project = Project.objects.get(pk=pk)  # Use pk to fetch the project directly
    except Project.DoesNotExist:
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    project_serializer = GetProjectSerializer(instance=project)
    return Response(project_serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_signatory_status(request, signatory_id):
    try:
        # Fetch the Signatories instance by ID
        signatory = Signatories.objects.get(pk=signatory_id)
    except Signatories.DoesNotExist:
        return Response({"error": "Signatory not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the new approval status from the request data
    new_status = request.data.get('approvalStatus')

    if new_status not in dict(Signatories.APPROVAL_CHOICES).keys():
        return Response({"error": "Invalid approval status."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the approval status
    signatory.approvalStatus = new_status
    
    # If the new status is approved, generate the signature code
    if new_status == 'approved':
        signatory.signatureCode = signatory.generate_signature_code()

    # Save the updated signatory instance
    signatory.save()

    return Response({"message": "Approval status updated successfully.", "signatureCode": signatory.signatureCode}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_regions(request):
    # Query all regions
    regions = Region.objects.all()

    # Serialize the regions
    region_serializer = RegionSerializer(regions, many=True)

    return Response(region_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_provinces(request, regionID):
    
    try:
        region = Region.objects.get(pk=regionID)
    except Region.DoesNotExist:
        return Response({"detail": "Region not found."}, status=status.HTTP_404_NOT_FOUND)
    
    provinces = Province.objects.filter(regionID=region)

    provinces_serializer = GetProvinceSerializer(provinces, many=True)

    return Response(provinces_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request, provinceID):

    try:
        province = Province.objects.get(pk=provinceID)
    except Province.DoesNotExist:
        return Response({"detail": "Province not found."}, status=status.HTTP_404_NOT_FOUND)

    cities = City.objects.filter(provinceID=province)

    cities_serializer = GetCitySerializer(cities, many=True)

    return Response(cities_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_barangays(request, cityID):

    try:
        city = City.objects.get(pk=cityID)
    except City.DoesNotExist:
        return Response({"detail": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    barangays = Barangay.objects.filter(cityID=city)

    barangays_serializer = GetBarangaySerializer(barangays, many=True)

    return Response(barangays_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_project_status(request, pk):
    # Get all projects for the user with userID equal to pk
    projects = Project.objects.filter(userID=pk)

    # Serialize the project data
    serializer = GetProjectStatusSerializer(projects, many=True)

    # Return the serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))