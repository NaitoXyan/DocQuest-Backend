from rest_framework import serializers
from docquestapp.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
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

class TargetGroupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = TargetGroup
        fields = ['targetGroupID', 'targetGroup', 'projectID']
    
class GoalsAndObjectivesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = GoalsAndObjectives
        fields = ['GAOID', 'goalsAndObjectives', 'projectID']

class MonitoringPlanAndScheduleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MonitoringPlanAndSchedule
        fields = ['MPASID', 'approach', 'dataGatheringStrategy', 'schedule', 'implementationPhase',
                  'projectID'
                  ]

class EvaluationAndMonitoringSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = EvaluationAndMonitoring
        fields = ['EAMID', 'projectSummary', 'indicators', 'meansOfVerification', 'risksAssumptions',
                  'type', 'projectID'
                  ]

class BudgetaryRequirementsItemsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = BudgetRequirementsItems
        fields = ['itemID', 'itemName', 'ustpAmount', 'partnerAmount', 'totalAmount', 'projectID']

class ProjectActivitiesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProjectActivities
        fields = ['projectActivitiesID', 'objective', 'involved', 'targetDate', 'personResponsibleID',
                  'projectID'
                  ]

class LoadingOfTrainersSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = LoadingOfTrainers
        fields = ['LOTID', 'userID', 'trainingLoad', 'hours', 'ustpBudget', 'agencyBudget', 'totalBudgetRequirement',
                  'projectID'
                  ]

class SignatoriesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Signatories
        fields = ['projectID', 'userID', 'approvalStatus']

class ProponentsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Proponents
        fields = ['projectID', 'userID']

class AddressSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Address
        fields = ['addressID', 'street', 'barangay', 'city', 'province', 'postalCode']

class PartnerAgencySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PartnerAgency
        fields = ['agencyID', 'agencyName', 'addressID']

class MOASerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MOA
        fields = ['moaID', 'partyADescription', 'partyBDescription', 'termination']

class WitnessethSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Witnesseth
        fields = ['witnessethID', 'whereas', 'moaID']

class PartyObligationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PartyObligation
        fields = ['poID', 'obligation', 'party', 'moaID']

class EffectivitySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Effectivity
        fields = ['effectiveID', 'effectivity', 'moaID']