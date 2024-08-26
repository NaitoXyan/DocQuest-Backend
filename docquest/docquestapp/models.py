from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class CustomUser(AbstractBaseUser):
    userID = models.AutoField(primary_key=True)
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
    firstname = models.CharField(max_length=150)
    middlename = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)

    USERNAME_FIELD = "email"

class Roles(models.Model):
    userID = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    projectLead = models.BooleanField(default=False)
    programChair = models.BooleanField(default=False)
    collegeDean = models.BooleanField(default=False)
    ECRDirector = models.BooleanField(default=False)
    VCAA = models.BooleanField(default=False)
    VCRI = models.BooleanField(default=False)
    accountant = models.BooleanField(default=False)
    chancellor = models.BooleanField(default=False)

class Address(models.Model):
    addressID = models.AutoField(primary_key=True)
    street = models.CharField(max_length=150)
    barangay = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    province = models.CharField(max_length=150)
    postal_code = models.CharField(max_length=10)

class PartnerAgency(models.Model):
    agencyID = models.AutoField(primary_key=True)
    agencyName = models.CharField(max_length=150)
    addressID = models.ForeignKey(Address, on_delete=models.CASCADE)

class MOA(models.Model):
    moaID = models.AutoField(primary_key=True)
    partyADescription = models.CharField()
    partyBDescription = models.CharField()
    termination = models.CharField()

class Witnesseth(models.Model):
    witnessethID = models.AutoField(primary_key=True)
    whereas = models.TextField()
    moaID = models.ForeignKey(MOA, on_delete=models.CASCADE)

class PartyObligation(models.Model):
    poID = models.AutoField(primary_key=True)
    obligation = models.TextField()
    party = models.TextField()
    moaID = models.ForeignKey(MOA, on_delete=models.CASCADE)

class Effectivity(models.Model):
    effectivityID = models.AutoField(primary_key=True)
    effectivity = models.TextField()
    moaID = models.ForeignKey(MOA, on_delete=models.CASCADE)

class Project(models.Model):
    projectID = models.AutoField(primary_key=True)
    programCategory = models.CharField(max_length=150)
    projectTitle = models.CharField(max_length=150)
    projectType = models.CharField(max_length=150)
    projectCategory = models.CharField(max_length=150)
    researchTitle = models.CharField(max_length=150)
    program = models.CharField(max_length=150)
    accreditationLevel = models.CharField(max_length=150)
    college = models.CharField(max_length=150)
    projectLocationID = models.ForeignKey(Address, on_delete=models.CASCADE) 
    agencyID = models.ForeignKey(PartnerAgency, on_delete=models.CASCADE)
    targetImplementation = models.DateField()
    totalHours = models.FloatField()
    background = models.CharField(max_length=150)
    projectComponent = models.CharField(max_length=150)
    beneficiaries = models.CharField(max_length=150)
    totalBudget = models.IntegerField()
    moaID = models.ForeignKey(MOA, on_delete=models.CASCADE)

class Signatories(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    approvalStatus = models.BooleanField(default=False)

class Proponents(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class TargetGroup(models.Model):
    targetGroupID = models.AutoField(primary_key=True)
    targetGroup = models.CharField()
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class GoalsAndObjectives(models.Model):
    GOAID = models.AutoField(primary_key=True)
    goalsAndObjectives = models.TextField()
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class LoadingOfTrainers(models.Model):
    LOTID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    trainingLoad = models.CharField(max_length=300)
    hours = models.FloatField()
    ustpBudget = models.IntegerField()
    agencyBudget = models.IntegerField()
    totalBudgetRequirement = models.IntegerField()
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class ProjectActivities(models.Model):
    projectActivitiesID = models.AutoField(primary_key=True)
    objective = models.TextField()
    involved = models.TextField()
    targetDate = models.DateField()
    personResponsibleID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class BudgetRequirementsItems(models.Model):
    itemID = models.AutoField(primary_key=True)
    itemName = models.CharField(max_length=150)
    ustpAmount = models.IntegerField()
    partnerAmount = models.IntegerField()
    totalAmount = models.IntegerField()
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class EvaluationAndMonitoring(models.Model):
    EAMID = models.AutoField(primary_key=True)
    projectSummary = models.TextField()
    indicators = models.TextField()
    meansOfVerification = models.TextField()
    risksAssumptions = models.TextField()
    type = models.CharField(max_length=100)
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class MonitoringPlanAndSchedule(models.Model):
    MPASID = models.AutoField(primary_key=True)
    approach = models.TextField()
    dataGatheringStrategy = models.TextField()
    schedule = models.TextField()
    implementationPhase = models.TextField()
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)