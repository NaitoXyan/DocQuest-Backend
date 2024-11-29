from rest_framework import serializers
from docquestapp.models import *
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ForeignObjectRel
from django.db import transaction

# mga nagamit
class UserSignupSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(many=True, queryset=Roles.objects.all())
    campus = serializers.PrimaryKeyRelatedField(queryset=Campus.objects.all(), write_only=True, required=False)
    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all(), write_only=True, required=False)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'firstname', 'middlename', 'lastname',
            'campus', 'college', 'program', 'contactNumber', 'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Extract non-user model fields
        roles = validated_data.pop('role')
        campus = validated_data.pop('campus', None)
        college = validated_data.pop('college', None)
        program = validated_data.pop('program', None)

        # Use transaction to ensure data consistency
        with transaction.atomic():
            # Create the user without setting password (since view handles it)
            password = validated_data.pop('password')  # Remove password from validated_data
            user = CustomUser(**validated_data)
            user.save()

            # Add roles
            user.role.set(roles)

            # If college/program info is provided, create Faculty record
            if any([college, program]):
                Faculty.objects.create(
                    userID=user,
                    collegeID=college,
                    programID=program
                )

        return user

    def validate(self, data):
        # Validate that if program is provided, college must also be provided
        if 'program' in data and not 'college' in data:
            raise serializers.ValidationError(
                {"college": "College must be provided when program is specified"}
            )

        # Validate that the program belongs to the specified college
        if 'program' in data and 'college' in data:
            if data['program'].collegeID != data['college']:
                raise serializers.ValidationError(
                    {"program": "Program must belong to the specified college"}
                )

        # Validate that the college belongs to the specified campus
        if 'college' in data and 'campus' in data:
            if data['college'].campusID != data['campus']:
                raise serializers.ValidationError(
                    {"college": "College must belong to the specified campus"}
                )

        return data

class UserEditProfileSerializer(serializers.ModelSerializer):
    # role = serializers.PrimaryKeyRelatedField(many=True, queryset=Roles.objects.all())

    class Meta(object):
        model = CustomUser
        fields = [
            'email', 'password', 'firstname', 'middlename', 'lastname',
            'contactNumber'
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

class BudgetRequirementsItemsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = BudgetRequirementsItems
        fields = ['itemName', 'ustpAmount', 'partnerAmount', 'totalAmount']

class ProjectActivitiesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProjectActivities
        fields = [
            'objective', 'involved', 'targetDate', 'personResponsible'
        ]

class ProjectManagementTeamSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProjectManagementTeam
        fields = ['name']

class LoadingOfTrainersSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = LoadingOfTrainers
        fields = [
            'faculty', 'trainingLoad', 'hours', 'ustpBudget', 'agencyBudget', 'totalBudgetRequirement'
        ]

class SignatoriesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Signatories
        fields = ['name', 'title']

class ProponentsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname']

class GetProponentsSerializer(serializers.ModelSerializer):
    role = RoleSerializer(many=True)
    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname', 'role']

class NonUserProponentsSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = NonUserProponents
        fields = ['name']

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

class ProjectMoaSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Project
        fields = ['moaID']

class WitnessethSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Witnesseth
        fields = ['witnessethID', 'whereas']

class PartyObligationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PartyObligation
        fields = ['poID', 'obligation', 'party']

class FirstPartySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = FirstParty
        fields = ['firstPartyID', 'name', 'title']

class SecondPartySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = SecondParty
        fields = ['secondPartyID', 'name', 'title']

class WitnessesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Witnesses
        fields = ['witnessID', 'name', 'title']

class GetSpecificMoaSerializer(serializers.ModelSerializer):
    witnesseth = WitnessethSerializer(many=True)
    partyObligation = PartyObligationSerializer(many=True)
    firstParty = FirstPartySerializer(many=True)
    secondParty = SecondPartySerializer(many=True)
    witnesses = WitnessesSerializer(many=True)
    
    class Meta(object):
        model = MOA
        fields = [
            'moaID', 'partyADescription', 'partyBDescription', 'coverageAndEffectivity', 'confidentialityClause',
            'termination', 'witnesseth', 'partyObligation', 'firstParty', 'secondParty', 'witnesses'
        ]

class PostMOASerializer(serializers.ModelSerializer):
    witnesseth = WitnessethSerializer(many=True)
    partyObligation = PartyObligationSerializer(many=True)
    firstParty = FirstPartySerializer(many=True)
    secondParty = SecondPartySerializer(many=True)
    witnesses = WitnessesSerializer(many=True)

    class Meta:
        model = MOA
        fields = [
            'moaID', 'partyADescription', 'partyBDescription', 'coverageAndEffectivity', 'confidentialityClause',
            'termination', 'witnesseth', 'partyObligation', 'firstParty', 'secondParty', 'witnesses'
        ]

    def create(self, validated_data):
        # Extract related data
        witnesseth_data = validated_data.pop('witnesseth')
        party_obligation_data = validated_data.pop('partyObligation')
        first_party_data = validated_data.pop('firstParty')
        second_party_data = validated_data.pop('secondParty')
        witnesses_data = validated_data.pop('witnesses')

        # Create MOA instance
        moa = MOA.objects.create(**validated_data)

        # Create related instances
        for witnesseth in witnesseth_data:
            Witnesseth.objects.create(moaID=moa, **witnesseth)
        
        for party_obligation in party_obligation_data:
            PartyObligation.objects.create(moaID=moa, **party_obligation)
        
        for first_party in first_party_data:
            FirstParty.objects.create(moaID=moa, **first_party)
        
        for second_party in second_party_data:
            SecondParty.objects.create(moaID=moa, **second_party)
        
        for witnesses in witnesses_data:
            Witnesses.objects.create(moaID=moa, **witnesses)

        return moa

class UpdateMOASerializer(serializers.ModelSerializer):
    witnesseth = WitnessethSerializer(many=True)
    partyObligation = PartyObligationSerializer(many=True)
    firstParty = FirstPartySerializer(many=True)
    secondParty = SecondPartySerializer(many=True)
    witnesses = WitnessesSerializer(many=True)

    class Meta:
        model = MOA
        fields = [
            'moaID', 'partyADescription', 'partyBDescription', 'coverageAndEffectivity', 'confidentialityClause',
            'termination', 'witnesseth', 'partyObligation', 'firstParty', 'secondParty', 'witnesses'
        ]
    
    def update(self, instance, validated_data):
        witnesseth_data = validated_data.pop('witnesseth')
        partyObligation_data = validated_data.pop('partyObligation')
        first_party_data = validated_data.pop('firstParty')
        second_party_data = validated_data.pop('secondParty')
        witnesses_data = validated_data.pop('witnesses')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
    
        # Clear existing related data on update
        instance.witnesseth.all().delete()
        instance.partyObligation.all().delete()
        instance.firstParty.all().delete()
        instance.secondParty.all().delete()
        instance.witnesses.all().delete()

        # Create related instances
        for witnesseth in witnesseth_data:
            Witnesseth.objects.create(moaID=instance, **witnesseth)
        
        for party_obligation in partyObligation_data:
            PartyObligation.objects.create(moaID=instance, **party_obligation)
        
        for first_party in first_party_data:
            FirstParty.objects.create(moaID=instance, **first_party)
        
        for second_party in second_party_data:
            SecondParty.objects.create(moaID=instance, **second_party)
        
        for witnesses in witnesses_data:
            Witnesses.objects.create(moaID=instance, **witnesses)
        
        instance.save()
        return instance

class GetProjectLeaderSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname']

class DeliverablesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Deliverables
        fields = ['deliverableID', 'deliverableName']

class UserProjectDeliverablesSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserProjectDeliverables
        fields = ['userID', 'projectID', 'deliverableID']

# class NotificationSerializer(serializers.ModelSerializer):
#     content_type = serializers.SlugRelatedField(
#         queryset=ContentType.objects.all(),
#         slug_field='model'  # Shows the model name as a string (e.g., 'project' or 'moa')
#     )

#     class Meta:
#         model = Notification
#         fields = [
#             'notificationID', 'userID', 'content_type',
#             'source_id', 'message', 'status', 'timestamp'
#         ]

class NotificationSerializer(serializers.ModelSerializer):
    source_type = serializers.SerializerMethodField()
    source_details = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['notificationID', 'message', 'status', 'timestamp', 'source_type', 'source_details']

    def get_source_type(self, obj):
        return obj.content_type.model

    def get_source_details(self, obj):
        # Return relevant details based on the source type
        if obj.source:
            if obj.content_type.model == 'project':
                return {
                    'id': obj.source.id,
                    'title': obj.source.title,  # Adjust based on your Project model
                }
            elif obj.content_type.model == 'moa':
                return {
                    'id': obj.source.id,
                    'name': obj.source.name,  # Adjust based on your MOA model
                }
        return None

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'reviewID', 'contentOwnerID', 'content_type', 'source_id',
            'reviewedByID', 'reviewStatus', 'reviewDate', 'comment',
            'collegeID', 'sequence'
        ]

class ProjectReviewSerializer(serializers.ModelSerializer):
    firstname = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()
    projectTitle = serializers.SerializerMethodField()
    dateCreated = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'reviewID', 'contentOwnerID', 'firstname', 'lastname',
            'content_type', 'content_type_name', 'source_id', 'projectTitle',
            'dateCreated', 'reviewedByID', 'reviewStatus', 'reviewDate', 'comment',
            'sequence', 'status'
        ]

    def get_firstname(self, obj):
        return obj.contentOwnerID.firstname

    def get_lastname(self, obj):
        return obj.contentOwnerID.lastname

    def get_projectTitle(self, obj):
        # Assumes source has a `projectTitle` field if the content type is Project
        return getattr(obj.source, 'projectTitle', 'N/A')

    def get_dateCreated(self, obj):
        # Assumes source has a `dateCreated` field
        return getattr(obj.source, 'dateCreated', None)

    def get_content_type_name(self, obj):
        # Fetch and return the name of the content type (e.g., 'Project' or 'MOA')
        return obj.content_type.model
    
    def get_status(self, obj):
        return getattr(obj.source, 'status', None)

class DocumentPDFSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model'  # Accepts model name (e.g., 'project' or 'moa')
    )

    class Meta:
        model = DocumentPDF
        fields = ['documentID', 'fileData', 'timestamp', 'content_type', 'source_id']

class ProgramCategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProgramCategory
        fields = ['programCategoryID', 'title']

class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = ProjectCategory
        fields = ['projectCategoryID', 'title']

class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = ['campusID', 'name']

class GetNameAndIDSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['userID', 'firstname', 'lastname']

class CollegeSerializer(serializers.ModelSerializer):
    campus = CampusSerializer(source='campusID', read_only=True)
    collegeDean = GetNameAndIDSerializer(read_only=True)

    class Meta(object):
        model = College
        fields = ['collegeID', 'abbreviation', 'title', 'collegeDean', 'campus']

class ProgramSerializer(serializers.ModelSerializer):
    college = CollegeSerializer(source='collegeID', read_only=True)
    programChair = GetNameAndIDSerializer(read_only=True)

    class Meta(object):
        model = Program
        fields = ['programID', 'abbreviation', 'title', 'programChair', 'college']

class GetProjectSerializer(serializers.ModelSerializer):
    userID = GetProjectLeaderSerializer()
    programCategory = ProgramCategorySerializer(many=True)
    projectCategory = ProjectCategorySerializer(many=True)
    program = ProgramSerializer(many=True)
    proponents = ProponentsSerializer(many=True)
    nonUserProponents = NonUserProponentsSerializer(many=True)
    projectLocationID = AddressSerializer()
    agency = PartnerAgencySerializer(many=True)
    goalsAndObjectives = GoalsAndObjectivesSerializer(many=True)
    projectActivities = ProjectActivitiesSerializer(many=True)
    projectManagementTeam = ProjectManagementTeamSerializer(many=True)
    budgetRequirements = BudgetRequirementsItemsSerializer(many=True)
    evaluationAndMonitorings = EvaluationAndMonitoringSerializer(many=True)
    monitoringPlanSchedules = MonitoringPlanAndScheduleSerializer(many=True)
    loadingOfTrainers = LoadingOfTrainersSerializer(many=True)
    signatories = SignatoriesSerializer(many=True)

    class Meta(object):
        model = Project
        fields = [
            'userID', 'programCategory', 'projectTitle', 'projectType', 'projectCategory', 'researchTitle', 'program', 
            'accreditationLevel', 'beneficiaries', 'targetStartDateImplementation', 'targetEndDateImplementation', 'totalHours',
            'background', 'projectComponent', 'targetScope', 'ustpBudget', 'partnerAgencyBudget', 'totalBudget', 'proponents', 
            'nonUserProponents', 'projectLocationID', 'agency', 'goalsAndObjectives', 'projectActivities', 'projectManagementTeam', 
            'budgetRequirements', 'evaluationAndMonitorings', 'monitoringPlanSchedules', 'loadingOfTrainers', 'signatories', 
            'dateCreated', 'status'
        ]

class PostProjectSerializer(serializers.ModelSerializer):
    userID = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    programCategory = serializers.PrimaryKeyRelatedField(queryset=ProgramCategory.objects.all(), many=True)
    projectCategory = serializers.PrimaryKeyRelatedField(queryset=ProjectCategory.objects.all(), many=True)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), many=True)
    proponents = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    nonUserProponents = NonUserProponentsSerializer(many=True)
    projectLocationID = PostAddressSerializer()
    agency = serializers.PrimaryKeyRelatedField(queryset=PartnerAgency.objects.all(), many=True)
    goalsAndObjectives = GoalsAndObjectivesSerializer(many=True)
    projectActivities = ProjectActivitiesSerializer(many=True)
    projectManagementTeam = ProjectManagementTeamSerializer(many=True)
    budgetRequirements = BudgetRequirementsItemsSerializer(many=True)
    evaluationAndMonitorings = EvaluationAndMonitoringSerializer(many=True)
    monitoringPlanSchedules = MonitoringPlanAndScheduleSerializer(many=True)
    loadingOfTrainers = LoadingOfTrainersSerializer(many=True, required=False)
    signatories = SignatoriesSerializer(many=True)

    class Meta(object):
        model = Project
        fields = [
            'userID', 'programCategory', 'projectTitle', 'projectType',
            'projectCategory', 'researchTitle', 'program', 'accreditationLevel', 'beneficiaries',  
            'targetStartDateImplementation', 'targetEndDateImplementation', 'totalHours', 'background', 'projectComponent', 'targetScope',
            'ustpBudget', 'partnerAgencyBudget', 'totalBudget', 'proponents', 'nonUserProponents', 'projectLocationID',
            'agency', 'goalsAndObjectives', 'projectActivities', 'projectManagementTeam', 'budgetRequirements',
            'evaluationAndMonitorings', 'monitoringPlanSchedules', 'loadingOfTrainers', 'signatories' 
        ]

    def create(self, validated_data):
        proponents_data = validated_data.pop('proponents')
        programCategory_data = validated_data.pop('programCategory')
        projectCategory_data = validated_data.pop('projectCategory')
        program_data = validated_data.pop('program')
        nonUserProponents_data = validated_data.pop('nonUserProponents')
        address_data = validated_data.pop('projectLocationID')
        projectLocationID = Address.objects.create(**address_data)
        agency_data = validated_data.pop('agency')
        goalsAndObjectives_data = validated_data.pop('goalsAndObjectives')
        projectActivities_data = validated_data.pop('projectActivities')
        projectManagementTeam_data = validated_data.pop('projectManagementTeam')
        budgetRequirements_data = validated_data.pop('budgetRequirements')
        evaluationAndMonitorings_data = validated_data.pop('evaluationAndMonitorings')
        monitoringPlanSchedules_data = validated_data.pop('monitoringPlanSchedules')
        loadingOfTrainers_data = validated_data.pop('loadingOfTrainers', [])
        signatories_data = validated_data.pop('signatories')
        
        project = Project.objects.create(projectLocationID=projectLocationID, **validated_data)

        project.agency.set(agency_data)
        project.proponents.set(proponents_data)

        project.programCategory.set(programCategory_data)
        project.projectCategory.set(projectCategory_data)
        project.program.set(program_data)

        for nonUserProponents_data in nonUserProponents_data:
            NonUserProponents.objects.create(project=project, **nonUserProponents_data)
        
        for goalsAndObjective_data in goalsAndObjectives_data:
            GoalsAndObjectives.objects.create(project=project, **goalsAndObjective_data)
        
        for projectActivity_data in projectActivities_data:
            ProjectActivities.objects.create(project=project, **projectActivity_data)

        for projectManagementTeam_data in projectManagementTeam_data:
            ProjectManagementTeam.objects.create(project=project, **projectManagementTeam_data)

        for budgetaryRequirement_data in budgetRequirements_data:
            BudgetRequirementsItems.objects.create(project=project, **budgetaryRequirement_data)

        for evaluationAndMonitoring_data in evaluationAndMonitorings_data:
            EvaluationAndMonitoring.objects.create(project=project, **evaluationAndMonitoring_data)

        for monitoringPlanSchedule_data in monitoringPlanSchedules_data:
            MonitoringPlanAndSchedule.objects.create(project=project, **monitoringPlanSchedule_data)

        for loadingOfTrainer_data in loadingOfTrainers_data:
            LoadingOfTrainers.objects.create(project=project, **loadingOfTrainer_data)

        for signatory_data in signatories_data:
            Signatories.objects.create(project=project, **signatory_data)

        return project

class UpdateProjectSerializer(serializers.ModelSerializer):
    userID = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    programCategory = serializers.PrimaryKeyRelatedField(queryset=ProgramCategory.objects.all(), many=True)
    projectCategory = serializers.PrimaryKeyRelatedField(queryset=ProjectCategory.objects.all(), many=True)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), many=True)
    proponents = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    nonUserProponents = NonUserProponentsSerializer(many=True)
    projectLocationID = PostAddressSerializer()
    agency = serializers.PrimaryKeyRelatedField(queryset=PartnerAgency.objects.all(), many=True)
    goalsAndObjectives = GoalsAndObjectivesSerializer(many=True)
    projectActivities = ProjectActivitiesSerializer(many=True)
    projectManagementTeam = ProjectManagementTeamSerializer(many=True)
    budgetRequirements = BudgetRequirementsItemsSerializer(many=True)
    evaluationAndMonitorings = EvaluationAndMonitoringSerializer(many=True)
    monitoringPlanSchedules = MonitoringPlanAndScheduleSerializer(many=True)
    loadingOfTrainers = LoadingOfTrainersSerializer(many=True, required=False)
    signatories = SignatoriesSerializer(many=True)

    class Meta(object):
        model = Project
        fields = [
            'userID', 'programCategory', 'projectTitle', 'projectType',
            'projectCategory', 'researchTitle', 'program', 'accreditationLevel', 'beneficiaries',  
            'targetImplementation', 'totalHours', 'background', 'projectComponent', 'targetScope',
            'ustpBudget', 'partnerAgencyBudget', 'totalBudget', 'proponents', 'nonUserProponents', 'projectLocationID',
            'agency', 'goalsAndObjectives', 'projectActivities', 'projectManagementTeam', 'budgetRequirements',
            'evaluationAndMonitorings', 'monitoringPlanSchedules', 'loadingOfTrainers', 'signatories' 
        ]

    def update(self, instance, validated_data):
        programCategory_data = validated_data.pop('programCategory')
        projectCategory_data = validated_data.pop('projectCategory')
        program_data = validated_data.pop('program')
        proponents_data = validated_data.pop('proponents')
        nonUserProponents_data = validated_data.pop('nonUserProponents')
        address_data = validated_data.pop('projectLocationID')
        agency_data = validated_data.pop('agency')
        goalsAndObjectives_data = validated_data.pop('goalsAndObjectives')
        projectActivities_data = validated_data.pop('projectActivities')
        projectManagementTeam_data = validated_data.pop('projectManagementTeam')
        budgetRequirements_data = validated_data.pop('budgetRequirements')
        evaluationAndMonitorings_data = validated_data.pop('evaluationAndMonitorings')
        monitoringPlanSchedules_data = validated_data.pop('monitoringPlanSchedules')
        loadingOfTrainers_data = validated_data.pop('loadingOfTrainers', [])
        signatories_data = validated_data.pop('signatories')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.agency.set(agency_data)
        instance.proponents.set(proponents_data)

        if address_data:
            for key, value in address_data.items():
                setattr(instance.projectLocationID, key, value)
            instance.projectLocationID.save()

        # Clear existing related data on update
        instance.programCategory.clear()
        instance.projectCategory.clear()
        instance.program.clear()
        instance.nonUserProponents.all().delete()
        instance.goalsAndObjectives.all().delete()
        instance.projectActivities.all().delete()
        instance.projectManagementTeam.all().delete()
        instance.budgetRequirements.all().delete()
        instance.evaluationAndMonitorings.all().delete()
        instance.monitoringPlanSchedules.all().delete()
        instance.loadingOfTrainers.all().delete()
        instance.signatories.all().delete()

        instance.programCategory.set(programCategory_data)
        instance.projectCategory.set(projectCategory_data)
        instance.program.set(program_data)

        for nonUserProponents_data in nonUserProponents_data:
            NonUserProponents.objects.create(project=instance, **nonUserProponents_data)
        
        for goalsAndObjective_data in goalsAndObjectives_data:
            GoalsAndObjectives.objects.create(project=instance, **goalsAndObjective_data)
        
        for projectActivity_data in projectActivities_data:
            ProjectActivities.objects.create(project=instance, **projectActivity_data)

        for projectManagementTeam_data in projectManagementTeam_data:
            ProjectManagementTeam.objects.create(project=instance, **projectManagementTeam_data)

        for budgetaryRequirement_data in budgetRequirements_data:
            BudgetRequirementsItems.objects.create(project=instance, **budgetaryRequirement_data)

        for evaluationAndMonitoring_data in evaluationAndMonitorings_data:
            EvaluationAndMonitoring.objects.create(project=instance, **evaluationAndMonitoring_data)

        for monitoringPlanSchedule_data in monitoringPlanSchedules_data:
            MonitoringPlanAndSchedule.objects.create(project=instance, **monitoringPlanSchedule_data)

        for loadingOfTrainer_data in loadingOfTrainers_data:
            LoadingOfTrainers.objects.create(project=instance, **loadingOfTrainer_data)

        for signatory_data in signatories_data:
            Signatories.objects.create(project=instance, **signatory_data)
        
        instance.save()
        return instance

class GetNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname']

class GetProjectStatusSerializer(serializers.ModelSerializer):
    projectUser = GetNameSerializer(source='userID', read_only=True)
    class Meta(object):
        model = Project
        fields = [
            'projectID', 'uniqueCode', 'projectTitle', 'dateCreated', 'status', 'projectUser'
        ]

class GetProjectTitleSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Project
        fields = ['projectTitle']

class GetMoaSerializer(serializers.ModelSerializer):
    moaUser = GetNameSerializer(source='userID', read_only=True)
    projectTitles = GetProjectTitleSerializer(source='projectMoa', many=True, read_only=True)
    
    class Meta(object):
        model = MOA
        fields = ['moaUser', 'moaID', 'uniqueCode', 'dateCreated', 'status', 'projectTitles']

class GetCampusSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Campus
        fields = ['campusID', 'name']

class GetCollegeDeanSerializer(serializers.ModelSerializer):
    collegeDean = GetNameAndIDSerializer(read_only=True)

    class Meta:
        model = College
        fields = ['collegeDean']

# Serializer to fetch program chair's name
class GetProgramChairSerializer(serializers.ModelSerializer):
    programChair = GetNameAndIDSerializer(read_only=True)

    class Meta:
        model = Program
        fields = ['programChair']

class GetAllProjectsSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(many=True)

    class Meta:
        model = Project
        fields = ['status', 'dateCreated', 'program']

class GetReviewsWithProjectIDSerializer(serializers.ModelSerializer):
    reviewedByID = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    college = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'reviewID', 'reviewedByID', 'college', 'program', 'fullname',
            'reviewStatus', 'reviewDate', 'comment', 'approvalCounter', 'reviewerResponsible'
        ]

    def get_college(self, obj):
        # Retrieve the related college if available
        if obj.collegeID:
            return obj.collegeID.title
        return None

    def get_program(self, obj):
        # Check if the reviewer is associated with a program
        reviewer = obj.reviewedByID
        program = Program.objects.filter(programChair=reviewer).first()
        return program.title if program else None

    def get_fullname(self, obj):
        # Concatenate the reviewer's full name
        reviewer = obj.reviewedByID
        return f"{reviewer.firstname} {reviewer.middlename} {reviewer.lastname}".strip()