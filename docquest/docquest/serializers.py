from rest_framework import serializers
from docquestapp.models import *
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer

# mga nagamit
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
        fields =  ['roleID', 'code', 'role']

class UserLoginSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, source='role')

    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname', 'roles']

class TargetGroupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = TargetGroup
        fields = ['targetGroup']
    
class GoalsAndObjectivesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = GoalsAndObjectives
        fields = ['goalsAndObjectives']

class MonitoringPlanAndScheduleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MonitoringPlanAndSchedule
        fields = [
            'approach', 'dataGatheringStrategy', 'schedule',
            'implementationPhase'
        ]

class EvaluationAndMonitoringSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = EvaluationAndMonitoring
        fields = [
            'projectSummary', 'indicators', 'meansOfVerification',
            'risksAssumptions', 'type'
        ]

class BudgetaryRequirementsItemsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = BudgetRequirementsItems
        fields = ['itemName', 'ustpAmount', 'partnerAmount', 'totalAmount']

class ProjectActivitiesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProjectActivities
        fields = [
            'objective', 'involved', 'targetDate', 'personResponsible'
        ]

class LoadingOfTrainersSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = LoadingOfTrainers
        fields = [
            'faculty', 'trainingLoad', 'hours', 'ustpBudget', 'agencyBudget', 'totalBudgetRequirement'
        ]

class SignatoriesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Signatories
        fields = ['userID', 'approvalStatus']

class ProponentsSerializer(serializers.ModelSerializer):
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

class GetProvinceSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Province
        fields = ['provinceID', 'province']

class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(source='provinceID', read_only=True)

    class Meta(object):
        model = City
        fields = ['cityID', 'city', 'postalCode', 'province']

class GetCitySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = City
        fields = ['cityID', 'city']

class BarangaySerializer(serializers.ModelSerializer):
    city = CitySerializer(source='cityID', read_only=True)

    class Meta(object):
        model = Barangay
        fields = ['barangayID', 'barangay', 'city']

class GetBarangaySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Barangay
        fields = ['barangayID', 'barangay']

class AddressSerializer(serializers.ModelSerializer):
    barangay = BarangaySerializer(source='barangayID', read_only=True)

    class Meta(object):
        model = Address
        fields = ['addressID', 'street', 'barangay']

class PostAddressSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Address
        fields = ['street', 'barangayID']

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
    targetGroups = TargetGroupSerializer(source='targetGroup', many=True)
    goalsAndObjectives = GoalsAndObjectivesSerializer(many=True)
    monitoringPlanSchedules = MonitoringPlanAndScheduleSerializer(source='monitoringPlanSched', many=True)
    evaluationAndMonitorings = EvaluationAndMonitoringSerializer(source='evalAndMonitoring', many=True)
    budgetaryRequirements = BudgetaryRequirementsItemsSerializer(source='budgetRequirements', many=True)
    projectActivities = ProjectActivitiesSerializer(many=True)
    loadingOfTrainers = LoadingOfTrainersSerializer(many=True)
    signatories = SignatoriesSerializer(source='signatoryProject', many=True)
    proponents = ProponentsSerializer(source='proponent', many=True)

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
    agency = serializers.PrimaryKeyRelatedField(queryset=PartnerAgency.objects.all(), many=True)

    projectLocationID = PostAddressSerializer()
    targetGroups = TargetGroupSerializer(many=True)
    goalsAndObjectives = GoalsAndObjectivesSerializer(many=True)
    monitoringPlanSchedules = MonitoringPlanAndScheduleSerializer(many=True)
    evaluationAndMonitorings = EvaluationAndMonitoringSerializer(many=True)
    budgetaryRequirements = BudgetaryRequirementsItemsSerializer(many=True)
    projectActivities = ProjectActivitiesSerializer(many=True)
    loadingOfTrainers = LoadingOfTrainersSerializer(many=True)
    signatories = SignatoriesSerializer(many=True)
    proponents = ProponentsSerializer(many=True)

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
        address_data = validated_data.pop('projectLocation')
        projectLocationID = Address.objects.create(**address_data)

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

        project = Project.objects.create(projectLocationID=projectLocationID, **validated_data)

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