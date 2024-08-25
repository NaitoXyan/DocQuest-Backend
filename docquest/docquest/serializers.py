from rest_framework import serializers
from docquestapp.models import *
# from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
<<<<<<< Updated upstream
        model = User
        fields = ['userID', 'email', 'password', 'firstname', 'middlename', 'lastname']
=======
        model = CustomUser
        fields = ['userID', 'email', 'password', 'firstname', 'middlename', 'lastname']

class RoleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Roles
        fields =  ['userID', 'projectLead', 'programChair', 'collegeDean', 'ECRDirector', 'VCAA', 'VCRI', 'accountant', 'chancellor']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Project
        fields = [
            'projectID', 'programCategory', 'projectTitle', 'projectType', 'projectCategory',
            'researchTitle', 'program', 'accreditationLevel', 'college', 'projectLocationID',
            'agencyID', 'targetImplementation', 'totalHours', 'background', 'projectComponent',
            'beneficiaries', 'totalBudget', 'moaID'
        ]
>>>>>>> Stashed changes
