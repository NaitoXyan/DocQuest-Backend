from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import datetime

class Roles(models.Model):
    roleID = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5)
    role = models.CharField(max_length=50, default='NO ROLE')

    class Meta:
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.role

class CustomUser(AbstractBaseUser, PermissionsMixin):
    userID = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    contactNumber = models.CharField(max_length=15, default="NO NUMBER")
    role = models.ManyToManyField(Roles, related_name='user')

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

class Campus(models.Model):
    campusID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Campuses"

class College(models.Model):
    collegeID = models.AutoField(primary_key=True)
    abbreviation = models.CharField(max_length=15)
    title = models.CharField(max_length=100)
    collegeDean = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True)
    campusID = models.ForeignKey(Campus, related_name='campus', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Colleges"

    def __str__(self):
        return self.title

class Program(models.Model):
    programID = models.AutoField(primary_key=True)
    abbreviation = models.CharField(max_length=15)
    title = models.CharField(max_length=100)
    programChair = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True)
    collegeID = models.ForeignKey(College, related_name='program', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.title

class Faculty(models.Model):
    facultyID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    collegeID = models.ForeignKey(College, on_delete=models.CASCADE)
    programID = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Faculties"

class Region(models.Model):
    regionID = models.AutoField(primary_key=True)
    region = models.CharField(max_length=50)

class Province(models.Model):
    provinceID = models.AutoField(primary_key=True)
    province = models.CharField(max_length=50)
    regionID = models.ForeignKey(Region, related_name='province', on_delete=models.CASCADE)

class City(models.Model):
    cityID = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    postalCode = models.IntegerField()
    provinceID = models.ForeignKey(Province, related_name='city', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Cities"

class Barangay(models.Model):
    barangayID = models.AutoField(primary_key=True)
    barangay = models.CharField(max_length=50)
    cityID = models.ForeignKey(City, related_name='barangay', on_delete=models.CASCADE)

class Address(models.Model):
    addressID = models.AutoField(primary_key=True)
    street = models.CharField(max_length=150)
    barangayID = models.ForeignKey(Barangay, related_name='address', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Addresses"

class PartnerAgency(models.Model):
    agencyID = models.AutoField(primary_key=True)
    agencyName = models.CharField(max_length=100)
    addressID = models.ForeignKey(Address, related_name='partnerAgency', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "Partner Agencies"

class MOA(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    moaID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, related_name='moaUser', on_delete=models.CASCADE)
    partyDescription = models.TextField()
    # partyBDescription = models.TextField()
    coverageAndEffectivity = models.TextField()
    confidentialityClause = models.TextField()
    termination = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    dateCreated = models.DateTimeField(auto_now_add=True)
    uniqueCode = models.CharField(max_length=255, unique=True, blank=True, null=True)
    approvalCounter = models.IntegerField(default=0)

class FirstParty(models.Model):
    firstPartyID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    moaID = models.ForeignKey(MOA, related_name='firstParty', on_delete=models.CASCADE)

class SecondParty(models.Model):
    secondPartyID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    moaID = models.ForeignKey(MOA, related_name='secondParty', on_delete=models.CASCADE)

class Witnesses(models.Model):
    witnessID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    moaID = models.ForeignKey(MOA, related_name='witnesses', on_delete=models.CASCADE)

class Witnesseth(models.Model):
    witnessethID = models.AutoField(primary_key=True)
    whereas = models.TextField()
    moaID = models.ForeignKey(MOA, related_name='witnesseth', on_delete=models.CASCADE)

class PartyObligation(models.Model):
    poID = models.AutoField(primary_key=True)
    obligation = models.TextField()
    party = models.TextField()
    moaID = models.ForeignKey(MOA, related_name='partyObligation', on_delete=models.CASCADE)

class ProgramCategory(models.Model):
    programCategoryID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Program Categories"

class ProjectCategory(models.Model):
    projectCategoryID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Project Categories"

class Project(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    projectID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, related_name='projectUser', on_delete=models.CASCADE)
    programCategory = models.ManyToManyField(ProgramCategory, related_name='programCategory') #1
    projectTitle = models.CharField(max_length=150) #2
    projectType = models.CharField(max_length=50) #3 
    projectCategory = models.ManyToManyField(ProjectCategory, related_name="projectCategory") #4
    researchTitle = models.CharField(max_length=150) #5
    program = models.ManyToManyField(Program, related_name='projectProgram') #6
    accreditationLevel = models.CharField(max_length=50) #7
    # college = models.CharField(max_length=50) #8
    beneficiaries = models.TextField() #9
    # targetImplementation = models.DateField() #10
    targetStartDateImplementation = models.DateField()
    targetEndDateImplementation = models.DateField()
    totalHours = models.FloatField() #11
    background = models.TextField() #12
    projectComponent = models.TextField() #13
    targetScope = models.TextField() #14
    ustpBudget = models.IntegerField(default=0) #15
    partnerAgencyBudget = models.IntegerField(default=0) #16
    totalBudget = models.IntegerField() #17
    projectLocationID = models.ForeignKey(Address, related_name='projectLocation', on_delete=models.CASCADE) #a2
    moaID = models.ForeignKey(MOA, related_name='projectMoa', on_delete=models.CASCADE, null=True)
    agency = models.ManyToManyField(PartnerAgency, related_name='projectAgency') #a3
    proponents = models.ManyToManyField(CustomUser, related_name='proponent')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    dateCreated = models.DateTimeField(auto_now_add=True)
    approvalCounter = models.IntegerField(default=0)
    uniqueCode = models.CharField(max_length=255, unique=True, blank=True, null=True)

class Signatories(models.Model): #print purpose
    project = models.ForeignKey(Project, related_name='signatories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)

class NonUserProponents(models.Model):
    project = models.ForeignKey(Project, related_name='nonUserProponents', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class Deliverables(models.Model):
    deliverableID = models.AutoField(primary_key=True)
    deliverableName = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Deliverables"

class UserProjectDeliverables(models.Model):
    userID = models.ForeignKey(CustomUser, related_name='userProjectDeliverables', on_delete=models.CASCADE)
    projectID = models.ForeignKey(Project, related_name='userProjectDeliverables', on_delete=models.CASCADE)
    deliverableID = models.ForeignKey(Deliverables, related_name='userProjectDeliverables', on_delete=models.CASCADE)

class Notification(models.Model):
    notificationID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, related_name='notification', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Refers to the model type (Project, MOA)
    source_id = models.PositiveIntegerField()  # ID of the related object (Project or MOA)
    source = GenericForeignKey('content_type', 'source_id')  # Polymorphic link to the related object
    message = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('Unread', 'Unread'), ('Read', 'Read')], default='Unread')
    timestamp = models.DateTimeField(auto_now_add=True)

class DocumentPDF(models.Model):
    documentID = models.AutoField(primary_key=True)
    fileData = models.BinaryField()
    timestamp = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Refers to the model type (Project, MOA)
    source_id = models.PositiveIntegerField()  # ID of the related object (Project or MOA)
    source = GenericForeignKey('content_type', 'source_id')  # Polymorphic link to the related object

class Review(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    reviewID = models.AutoField(primary_key=True)
    contentOwnerID = models.ForeignKey(CustomUser, related_name='reviewsContentOwner', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Refers to the model type (Project, MOA)
    source_id = models.PositiveIntegerField()  # ID of the related object (Project or MOA)
    source = GenericForeignKey('content_type', 'source_id')  # Polymorphic link to the related object
    reviewedByID = models.ForeignKey(CustomUser, related_name='reviewsReviewedBy', on_delete=models.CASCADE)
    reviewStatus = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewDate = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)
    approvalCounter = models.IntegerField(default=0)
    reviewerResponsible = models.CharField(max_length=10, blank=True, null=True)

    # New fields for college-specific reviews
    collegeID = models.ForeignKey('College', on_delete=models.CASCADE, null=True, blank=True)
    sequence = models.PositiveIntegerField(default=0)  # Group all reviewers of a college under the same sequence

class GoalsAndObjectives(models.Model): #a5
    GAOID = models.AutoField(primary_key=True)
    goalsAndObjectives = models.TextField()
    project = models.ForeignKey(Project, related_name='goalsAndObjectives', on_delete=models.CASCADE)

class LoadingOfTrainers(models.Model):
    LOTID = models.AutoField(primary_key=True)
    faculty = models.CharField(max_length=50)
    trainingLoad = models.TextField()
    hours = models.FloatField()
    ustpBudget = models.IntegerField()
    agencyBudget = models.IntegerField()
    totalBudgetRequirement = models.IntegerField()
    project = models.ForeignKey(Project, related_name='loadingOfTrainers', on_delete=models.CASCADE,blank=True, null=True)

class ProjectActivities(models.Model): #a6
    projectActivitiesID = models.AutoField(primary_key=True)
    objective = models.TextField()
    involved = models.TextField()
    targetDate = models.DateField()
    personResponsible = models.TextField()
    project = models.ForeignKey(Project, related_name='projectActivities', on_delete=models.CASCADE)

class ProjectManagementTeam(models.Model): #a7
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, related_name='projectManagementTeam', on_delete=models.CASCADE)

class BudgetRequirementsItems(models.Model): #a8
    itemID = models.AutoField(primary_key=True)
    itemName = models.CharField(max_length=50)
    ustpAmount = models.IntegerField()
    partnerAmount = models.IntegerField()
    totalAmount = models.IntegerField()
    project = models.ForeignKey(Project, related_name='budgetRequirements', on_delete=models.CASCADE)

class EvaluationAndMonitoring(models.Model): #a9
    EAMID = models.AutoField(primary_key=True)
    projectSummary = models.TextField(null=True, blank=True)
    indicators = models.TextField(null=True, blank=True)
    meansOfVerification = models.TextField(null=True, blank=True)
    risksAssumptions = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100)
    project = models.ForeignKey(Project, related_name='evaluationAndMonitorings', on_delete=models.CASCADE)

class MonitoringPlanAndSchedule(models.Model): #a10
    MPASID = models.AutoField(primary_key=True)
    approach = models.TextField()
    dataGatheringStrategy = models.TextField()
    schedule = models.TextField()
    implementationPhase = models.TextField()
    project = models.ForeignKey(Project, related_name='monitoringPlanSchedules', on_delete=models.CASCADE)