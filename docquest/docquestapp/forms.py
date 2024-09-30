from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

class RoleCreationForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = "__all__"