from rest_framework import serializers
from docquestapp.models import *
# from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['userID', 'email', 'password', 'firstname', 'middlename', 'lastname']