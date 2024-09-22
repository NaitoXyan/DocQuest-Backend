from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager

class Roles(models.Model):
    roleID = models.AutoField(primary_key=True)
    role = models.CharField(max_length=30, default='NO ROLE')

class CustomUser(AbstractBaseUser):
    userID = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    campus = models.CharField(max_length=50, default="NO CAMPUS SELECTED")
    college = models.CharField(max_length=50, default="NO COLLEGE SELECTED")
    department = models.CharField(max_length=50, default="NO DEPARTMENT SELECTED")
    contactNumber = models.CharField(max_length=15, default="NO NUMBER")
    role = models.ManyToManyField(Roles)

    objects = UserManager()
    
    USERNAME_FIELD = "email"

class Region(models.Model):
    regionID = models.AutoField(primary_key=True)
    region = models.CharField(max_length=15)

class Province(models.Model):
    provinceID = models.AutoField(primary_key=True)
    province = models.CharField(max_length=30)
    regionID = models.ForeignKey(Region, on_delete=models.CASCADE)

class City(models.Model):
    cityID = models.AutoField(primary_key=True)
    city = models.CharField(max_length=30)
    postalCode = models.IntegerField()
    provinceID = models.ForeignKey(Province, on_delete=models.CASCADE)

class Barangay(models.Model):
    barangayID = models.AutoField(primary_key=True)
    barangay = models.CharField(max_length=30)
    cityID = models.ForeignKey(City, on_delete=models.CASCADE)

class Address(models.Model):
    addressID = models.AutoField(primary_key=True)
    street = models.CharField(max_length=150)
    barangayID = models.ForeignKey(Barangay, on_delete=models.CASCADE)

class PartnerAgency(models.Model):
    agencyID = models.AutoField(primary_key=True)
    agencyName = models.CharField(max_length=100)
    addressID = models.ForeignKey(Address, on_delete=models.CASCADE)

class MOA(models.Model):
    moaID = models.AutoField(primary_key=True)
    partyADescription = models.TextField()
    partyBDescription = models.TextField()
    termination = models.TextField()

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
    programCategory = models.CharField(max_length=50)
    projectTitle = models.CharField(max_length=150)
    projectType = models.CharField(max_length=50)
    projectCategory = models.CharField(max_length=100)
    researchTitle = models.CharField(max_length=150)
    program = models.CharField(max_length=150)
    accreditationLevel = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    projectLocationID = models.ForeignKey(Address, on_delete=models.CASCADE) 
    agency = models.ManyToManyField(PartnerAgency)
    targetImplementation = models.DateField()
    totalHours = models.FloatField()
    background = models.TextField()
    projectComponent = models.TextField()
    beneficiaries = models.TextField()
    totalBudget = models.IntegerField()
    moaID = models.ForeignKey(MOA, on_delete=models.CASCADE)
    proponents = models.ManyToManyField(CustomUser)

class Signatories(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    approvalStatus = models.BooleanField(default=False)

# class Proponents(models.Model):
#     projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
#     userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class TargetGroup(models.Model):
    targetGroupID = models.AutoField(primary_key=True)
    targetGroup = models.CharField(max_length=200)
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class GoalsAndObjectives(models.Model):
    GAOID = models.AutoField(primary_key=True)
    goalsAndObjectives = models.TextField()
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)

class LoadingOfTrainers(models.Model):
    LOTID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    trainingLoad = models.TextField()
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
    itemName = models.CharField(max_length=50)
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