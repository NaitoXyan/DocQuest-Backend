from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
import datetime
import hashlib

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
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    projectID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(CustomUser, related_name='projectUser', on_delete=models.CASCADE)
    programCategory = models.CharField(max_length=50) #1
    projectTitle = models.CharField(max_length=150) #2
    projectType = models.CharField(max_length=50) #3 
    projectCategory = models.CharField(max_length=100) #4
    researchTitle = models.CharField(max_length=150) #5
    program = models.CharField(max_length=150) #6
    accreditationLevel = models.CharField(max_length=50) #7
    college = models.CharField(max_length=50) #8
    beneficiaries = models.TextField() #9
    targetImplementation = models.DateField() #10
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

    routingProgress = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    dateCreated = models.DateTimeField(auto_now_add=True)

    uniqueCode = models.CharField(max_length=255, unique=True, blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     # Save the instance first to ensure projectID is generated.
    #     super(Project, self).save(*args, **kwargs)

    #     # Generate the unique code if it hasn't been set yet.
    #     if not self.uniqueCode:
    #         self.uniqueCode = f"{self.projectID}-{self.dateCreated.strftime('%Y%m%d')}"

    #     # Update project status based on routingProgress
    #     if self.routingProgress >= 7:
    #         self.status = 'approved'
    #     elif self.status != 'rejected':  # Do not change to pending if already rejected
    #         self.status = 'pending'

    #     # Save the instance again if there are changes.
    #     super(Project, self).save(*args, **kwargs)

class Signatories(models.Model):
    APPROVAL_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('none', 'None'),
    ]
    
    project = models.ForeignKey(Project, related_name='signatoryProject', on_delete=models.CASCADE)
    userID = models.ForeignKey(CustomUser, related_name='signatoryUser', on_delete=models.CASCADE)
    signatureCode = models.CharField(max_length=255)
    approvalStatus = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='none')

    def generate_signature_code(self):
        """
        Generate the signature code in the format userId-projectId-date+checksum.
        """
        date_str = self.project.dateCreated.strftime('%Y%m%d')  # Convert dateCreated to YYYYMMDD
        code_without_checksum = f"{self.userID.pk}-{self.project.projectID}-{date_str}"
        checksum = self.calculate_checksum(code_without_checksum)
        return f"{code_without_checksum}+{checksum}"

    def calculate_checksum(self, code):
        """
        Calculate a checksum using a simple hash (or sum of ASCII values).
        """
        return sum(ord(char) for char in code) % 10  # Simple checksum (mod 10)

    def save(self, *args, **kwargs):
        # Handle approval status logic
        if self.approvalStatus == 'approved':
            # Generate the signatureCode only when approvalStatus is approved
            if not self.signatureCode:
                self.signatureCode = self.generate_signature_code()

            # Increment the routingProgress of the associated project
            self.project.routingProgress += 1

        elif self.approvalStatus == 'rejected':
            # If rejected, set project status to 'rejected'
            self.project.status = 'rejected'
            # Ensure routingProgress doesn't get updated further once rejected
            self.project.routingProgress = min(self.project.routingProgress, 7)

        # Save the project with the updated routingProgress and status
        self.project.save()

        # Call the super method to save the Signatories instance
        super(Signatories, self).save(*args, **kwargs)

    def __str__(self):
        return self.signatureCode if self.signatureCode else "No signature code"

class Proponents(models.Model): #a1
    project = models.ForeignKey(Project, related_name='proponent', on_delete=models.CASCADE)
    proponent = models.CharField(max_length=50)

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
    project = models.ForeignKey(Project, related_name='loadingOfTrainers', on_delete=models.CASCADE)

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
    projectSummary = models.TextField(default="Empty")
    indicators = models.TextField(default="Empty")
    meansOfVerification = models.TextField(default="Empty")
    risksAssumptions = models.TextField(default="Empty")
    type = models.CharField(max_length=100, default="Empty")
    project = models.ForeignKey(Project, related_name='evalAndMonitoring', on_delete=models.CASCADE)

class MonitoringPlanAndSchedule(models.Model): #a10
    MPASID = models.AutoField(primary_key=True)
    approach = models.TextField()
    dataGatheringStrategy = models.TextField()
    schedule = models.TextField()
    implementationPhase = models.TextField()
    project = models.ForeignKey(Project, related_name='monitoringPlanSched', on_delete=models.CASCADE)