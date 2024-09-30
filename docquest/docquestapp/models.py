from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin

class Roles(models.Model):
    roleID = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4)
    role = models.CharField(max_length=50, default='NO ROLE')

    def __str__(self):
        return self.role

class CustomUser(AbstractBaseUser, PermissionsMixin):
    userID = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    campus = models.CharField(max_length=50, default="NO CAMPUS SELECTED")
    college = models.CharField(max_length=50, default="NO COLLEGE SELECTED")
    department = models.CharField(max_length=50, default="NO DEPARTMENT SELECTED")
    contactNumber = models.CharField(max_length=15, default="NO NUMBER")
    role = models.ManyToManyField(Roles, related_name='user')

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

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

class Barangay(models.Model):
    barangayID = models.AutoField(primary_key=True)
    barangay = models.CharField(max_length=50)
    cityID = models.ForeignKey(City, related_name='barangay', on_delete=models.CASCADE)

class Address(models.Model):
    addressID = models.AutoField(primary_key=True)
    street = models.CharField(max_length=150)
    barangayID = models.ForeignKey(Barangay, related_name='address', on_delete=models.CASCADE)

class PartnerAgency(models.Model):
    agencyID = models.AutoField(primary_key=True)
    agencyName = models.CharField(max_length=100)
    addressID = models.ForeignKey(Address, related_name='partnerAgency', on_delete=models.CASCADE)

class MOA(models.Model):
    moaID = models.AutoField(primary_key=True)
    partyADescription = models.TextField()
    partyBDescription = models.TextField()
    termination = models.TextField()

class Witnesseth(models.Model):
    witnessethID = models.AutoField(primary_key=True)
    whereas = models.TextField()
    moaID = models.ForeignKey(MOA, related_name='witnesseth', on_delete=models.CASCADE)

class PartyObligation(models.Model):
    poID = models.AutoField(primary_key=True)
    obligation = models.TextField()
    party = models.TextField()
    moaID = models.ForeignKey(MOA, related_name='partyObligation', on_delete=models.CASCADE)

class Effectivity(models.Model):
    effectivityID = models.AutoField(primary_key=True)
    effectivity = models.TextField()
    moaID = models.ForeignKey(MOA, related_name='effectivity', on_delete=models.CASCADE)

class Project(models.Model):
    projectID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, related_name='projectUser', on_delete=models.CASCADE)
    programCategory = models.CharField(max_length=50)
    projectTitle = models.CharField(max_length=150)
    projectType = models.CharField(max_length=50)
    projectCategory = models.CharField(max_length=100)
    researchTitle = models.CharField(max_length=150)
    program = models.CharField(max_length=150)
    accreditationLevel = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    projectLocationID = models.ForeignKey(Address, related_name='projectLocation', on_delete=models.CASCADE) 
    agency = models.ManyToManyField(PartnerAgency, related_name='projectAgency')
    targetImplementation = models.DateField()
    totalHours = models.FloatField()
    background = models.TextField()
    projectComponent = models.TextField()
    beneficiaries = models.TextField()
    totalBudget = models.IntegerField()
    moaID = models.ForeignKey(MOA, related_name='projectMoa', on_delete=models.CASCADE, null=True)

class Signatories(models.Model):
    project = models.ForeignKey(Project, related_name='signatoryProject', on_delete=models.CASCADE)
    userID = models.ForeignKey(CustomUser, related_name='signatoryUser', on_delete=models.CASCADE)
    approvalStatus = models.BooleanField(default=False)

class Proponents(models.Model):
    project = models.ForeignKey(Project, related_name='proponent', on_delete=models.CASCADE)
    proponent = models.CharField(max_length=50)

class TargetGroup(models.Model):
    targetGroupID = models.AutoField(primary_key=True)
    targetGroup = models.CharField(max_length=200)
    project = models.ForeignKey(Project, related_name='targetGroup', on_delete=models.CASCADE)

class GoalsAndObjectives(models.Model):
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
    project = models.ForeignKey(Project, related_name='loadingOfTrainers', on_delete=models.CASCADE)

class ProjectActivities(models.Model):
    projectActivitiesID = models.AutoField(primary_key=True)
    objective = models.TextField()
    involved = models.TextField()
    targetDate = models.DateField()
    personResponsibleID = models.CharField(max_length=50)
    project = models.ForeignKey(Project, related_name='projectActivities', on_delete=models.CASCADE)

class BudgetRequirementsItems(models.Model):
    itemID = models.AutoField(primary_key=True)
    itemName = models.CharField(max_length=50)
    ustpAmount = models.IntegerField()
    partnerAmount = models.IntegerField()
    totalAmount = models.IntegerField()
    project = models.ForeignKey(Project, related_name='budgetRequirements', on_delete=models.CASCADE)

class EvaluationAndMonitoring(models.Model):
    EAMID = models.AutoField(primary_key=True)
    projectSummary = models.TextField()
    indicators = models.TextField()
    meansOfVerification = models.TextField()
    risksAssumptions = models.TextField()
    type = models.CharField(max_length=100)
    project = models.ForeignKey(Project, related_name='evalAndMonitoring', on_delete=models.CASCADE)

class MonitoringPlanAndSchedule(models.Model):
    MPASID = models.AutoField(primary_key=True)
    approach = models.TextField()
    dataGatheringStrategy = models.TextField()
    schedule = models.TextField()
    implementationPhase = models.TextField()
    project = models.ForeignKey(Project, related_name='monitoringPlanSched', on_delete=models.CASCADE)