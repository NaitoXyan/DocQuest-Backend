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

class CustomUserForm(forms.ModelForm):
    campus = forms.ModelChoiceField(queryset=Campus.objects.all(), required=False)
    college = forms.ModelChoiceField(queryset=College.objects.all(), required=False)
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=False)
    
    class Meta:
        model = CustomUser
        fields = ["email", "password", "firstname", "middlename", "lastname",
                 "contactNumber", "role", "campus", "college", "program"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Try to get faculty info if it exists
            try:
                faculty = Faculty.objects.get(userID=self.instance)
                self.initial['college'] = faculty.collegeID
                self.initial['program'] = faculty.programID
                if faculty.collegeID:
                    self.initial['campus'] = faculty.collegeID.campusID
            except Faculty.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        program = cleaned_data.get('program')
        college = cleaned_data.get('college')
        campus = cleaned_data.get('campus')

        if program and not college:
            raise forms.ValidationError("College must be specified when program is selected")

        if program and college and program.collegeID != college:
            raise forms.ValidationError("Selected program must belong to the selected college")

        if college and campus and college.campusID != campus:
            raise forms.ValidationError("Selected college must belong to the selected campus")

        return cleaned_data
    
    def clean_role(self):
        roles = self.cleaned_data.get("role")
        unique_role_codes = ["ecrd", "vpala"]  # Codes for unique roles

        for role_code in unique_role_codes:
            unique_role = Roles.objects.filter(code=role_code).first()
            if unique_role and unique_role in roles:
                # Check if the unique role is already assigned to another user
                conflicting_users = CustomUser.objects.filter(role=unique_role).exclude(pk=self.instance.pk)
                if conflicting_users.exists():
                    raise ValidationError(
                        f"The role '{unique_role.name}' (code: {role_code}) is already assigned to another user."
                    )
        return roles