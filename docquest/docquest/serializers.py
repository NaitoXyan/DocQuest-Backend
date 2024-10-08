from rest_framework import serializers
from docquestapp.models import *
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer

# mga nagamit
class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = (
            'email', 'password', 'firstname', 'middlename', 'lastname',
            'campus', 'college', 'department', 'contactNumber', 'role',
        )

class UserSignupSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(many=True, queryset=Roles.objects.all())

    class Meta(object):
        model = CustomUser
        fields = [
            'email', 'password', 'firstname', 'middlename', 'lastname',
            'campus', 'college', 'department', 'contactNumber', 'role'
        ]

class UserEditProfileSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(many=True, queryset=Roles.objects.all())

    class Meta(object):
        model = CustomUser
        fields = [
            'email', 'password', 'firstname', 'middlename', 'lastname',
            'campus', 'college', 'department', 'contactNumber', 'role'
        ]

class RoleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Roles
        fields =  ['role']

class SetRoleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields =  ['role']

class UserLoginSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, source='role')

    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname', 'roles']

class PostTargetGroupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = TargetGroup
        fields = ['targetGroup']
    
class PostGoalsAndObjectivesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = GoalsAndObjectives
        fields = ['goalsAndObjectives']

class PostMonitoringPlanAndScheduleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MonitoringPlanAndSchedule
        fields = [
            'approach', 'dataGatheringStrategy', 'schedule',
            'implementationPhase'
        ]

class PostEvaluationAndMonitoringSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = EvaluationAndMonitoring
        fields = [
            'projectSummary', 'indicators', 'meansOfVerification',
            'risksAssumptions', 'type'
        ]

class PostBudgetaryRequirementsItemsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = BudgetRequirementsItems
        fields = ['itemName', 'ustpAmount', 'partnerAmount', 'totalAmount']

class PostProjectActivitiesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProjectActivities
        fields = [
            'objective', 'involved', 'targetDate', 'personResponsibleID'
        ]

class PostLoadingOfTrainersSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = LoadingOfTrainers
        fields = [
            'faculty', 'trainingLoad', 'hours', 'ustpBudget', 'agencyBudget', 'totalBudgetRequirement'
        ]

class PostSignatoriesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Signatories
        fields = ['userID', 'approvalStatus']

class PostProponentsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Proponents
        fields = ['proponent']

class RegionSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Region
        fields = ['regionID', 'region']

class ProvinceSerializer(serializers.ModelSerializer):
    region = RegionSerializer(source='regionID', read_only=True)

    class Meta(object):
        model = Province
        fields = ['provinceID', 'province', 'region']

class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(source='provinceID', read_only=True)

    class Meta(object):
        model = City
        fields = ['cityID', 'city', 'postalCode', 'province']

class BarangaySerializer(serializers.ModelSerializer):
    city = CitySerializer(source='cityID', read_only=True)

    class Meta(object):
        model = Barangay
        fields = ['barangayID', 'barangay', 'city']

class AddressSerializer(serializers.ModelSerializer):
    barangay = BarangaySerializer(source='barangayID', read_only=True)

    class Meta(object):
        model = Address
        fields = ['addressID', 'street', 'barangay']

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

class GetProjectLeaderSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname']

class GetProjectSerializer(serializers.ModelSerializer):
    userID = GetProjectLeaderSerializer()
    projectLocationID = AddressSerializer()
    agency = PartnerAgencySerializer(many=True)

    targetGroups = PostTargetGroupSerializer(source='targetGroup', many=True)
    goalsAndObjectives = PostGoalsAndObjectivesSerializer(many=True)
    monitoringPlanSchedules = PostMonitoringPlanAndScheduleSerializer(source='monitoringPlanSched', many=True)
    evaluationAndMonitorings = PostEvaluationAndMonitoringSerializer(source='evalAndMonitoring', many=True)
    budgetaryRequirements = PostBudgetaryRequirementsItemsSerializer(source='budgetRequirements', many=True)
    projectActivities = PostProjectActivitiesSerializer(many=True)
    loadingOfTrainers = PostLoadingOfTrainersSerializer(many=True)
    signatories = PostSignatoriesSerializer(source='signatoryProject', many=True)
    proponents = PostProponentsSerializer(source='proponent', many=True)

    class Meta(object):
        model = Project
        fields = [
            'userID', 'programCategory', 'projectTitle', 'projectType',
            'projectCategory', 'researchTitle', 'program', 'accreditationLevel',
            'college', 'projectLocationID', 'agency', 'targetImplementation',
            'totalHours', 'background', 'projectComponent', 'beneficiaries',
            'totalBudget', 'targetGroups', 'goalsAndObjectives', 'monitoringPlanSchedules',
            'evaluationAndMonitorings', 'budgetaryRequirements', 'projectActivities',
            'loadingOfTrainers', 'signatories', 'proponents'
        ]

class PostProjectSerializer(serializers.ModelSerializer):
    userID = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    projectLocationID = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    agency = serializers.PrimaryKeyRelatedField(queryset=PartnerAgency.objects.all(), many=True)

    targetGroups = PostTargetGroupSerializer(many=True)
    goalsAndObjectives = PostGoalsAndObjectivesSerializer(many=True)
    monitoringPlanSchedules = PostMonitoringPlanAndScheduleSerializer(many=True)
    evaluationAndMonitorings = PostEvaluationAndMonitoringSerializer(many=True)
    budgetaryRequirements = PostBudgetaryRequirementsItemsSerializer(many=True)
    projectActivities = PostProjectActivitiesSerializer(many=True)
    loadingOfTrainers = PostLoadingOfTrainersSerializer(many=True)
    signatories = PostSignatoriesSerializer(many=True)
    proponents = PostProponentsSerializer(many=True)

    class Meta(object):
        model = Project
        fields = [
            'userID', 'programCategory', 'projectTitle', 'projectType',
            'projectCategory', 'researchTitle', 'program', 'accreditationLevel',
            'college', 'projectLocationID', 'agency', 'targetImplementation',
            'totalHours', 'background', 'projectComponent', 'beneficiaries',
            'totalBudget', 'targetGroups', 'goalsAndObjectives', 'monitoringPlanSchedules',
            'evaluationAndMonitorings', 'budgetaryRequirements', 'projectActivities',
            'loadingOfTrainers', 'signatories', 'proponents'
        ]

    def create(self, validated_data): 
        targetGroups_data = validated_data.pop('targetGroups')
        goalsAndObjectives_data = validated_data.pop('goalsAndObjectives')
        monitoringPlanSchedules_data = validated_data.pop('monitoringPlanSchedules')
        evaluationAndMonitorings_data = validated_data.pop('evaluationAndMonitorings')
        budgetaryRequirements_data = validated_data.pop('budgetaryRequirements')
        projectActivities_data = validated_data.pop('projectActivities')
        loadingOfTrainers_data = validated_data.pop('loadingOfTrainers')
        signatories_data = validated_data.pop('signatories')
        proponents_data = validated_data.pop('proponents')

        agency_data = validated_data.pop('agency')

        project = Project.objects.create(**validated_data)

        project.agency.set(agency_data)

        for targetGroup_data in targetGroups_data:
            TargetGroup.objects.create(project=project, **targetGroup_data)
        
        for goalsAndObjective_data in goalsAndObjectives_data:
            GoalsAndObjectives.objects.create(project=project, **goalsAndObjective_data)

        for monitoringPlanSchedule_data in monitoringPlanSchedules_data:
            MonitoringPlanAndSchedule.objects.create(project=project, **monitoringPlanSchedule_data)

        for evaluationAndMonitoring_data in evaluationAndMonitorings_data:
            EvaluationAndMonitoring.objects.create(project=project, **evaluationAndMonitoring_data)

        for budgetaryRequirement_data in budgetaryRequirements_data:
            BudgetRequirementsItems.objects.create(project=project, **budgetaryRequirement_data)

        for projectActivity_data in projectActivities_data:
            ProjectActivities.objects.create(project=project, **projectActivity_data)

        for loadingOfTrainer_data in loadingOfTrainers_data:
            LoadingOfTrainers.objects.create(project=project, **loadingOfTrainer_data)

        for signatory_data in signatories_data:
            Signatories.objects.create(project=project, **signatory_data)

        for proponent_data in proponents_data:
            Proponents.objects.create(project=project, **proponent_data)

        return project