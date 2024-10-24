from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import *
from .models import *

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ("email", "is_staff", "is_active",)
#     list_filter = ("email", "is_staff", "is_active",)
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
#     )
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": (
#                 "email", "password1", "password2", "is_staff",
#                 "is_active", "groups", "user_permissions"
#             )}
#         ),
#     )
#     search_fields = ("email",)
#     ordering = ("email",)

class CreateUserAdmin(admin.ModelAdmin):
    fields = ["email", "password", "firstname", "middlename", "lastname",
              "campus", "college", "department", "contactNumber", "role"
    ]
    list_display = ["userID", "firstname", "lastname", "display_roles"]

    # Create a method to display roles as a comma-separated string
    def display_roles(self, obj):
        return ", ".join([role.role for role in obj.role.all()])
    
    display_roles.short_description = 'Roles'  # Customize column header

class RolesAdmin(admin.ModelAdmin):
    form = RoleCreationForm

    fields = ["role", "code"]
    list_display = ["roleID", "role", "code"]

class SignatoriesAdmin(admin.ModelAdmin):
    fields = ["project", "userID", "signatureCode", "approvalStatus"]
    list_display = ["project", "userID", "signatureCode", "approvalStatus"]

class RegionAdmin(admin.ModelAdmin):
    fields = ["region"]
    list_display = ["regionID", "region"]

class ProvinceAdmin(admin.ModelAdmin):
    fields = ["province", "regionID"]
    list_display = ["provinceID", "province", "regionID"]

class CityAdmin(admin.ModelAdmin):
    fields = ["city", "postalCode", "provinceID"]
    list_display = ["cityID", "city", "postalCode", "provinceID"]

class BarangayAdmin(admin.ModelAdmin):
    fields = ["barangay", "cityID"]
    list_display = ["barangayID", "barangay", "cityID"]

class AddressAdmin(admin.ModelAdmin):
    fields = ["street", "barangayID"]
    list_display = ["addressID", "street", "barangayID"]

class PartnerAgencyAdmin(admin.ModelAdmin):
    fields = ["agencyName", "addressID"]
    list_display = ["agencyID", "agencyName", "addressID"]

# admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Roles, RolesAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Barangay, BarangayAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PartnerAgency, PartnerAgencyAdmin)
admin.site.register(CustomUser, CreateUserAdmin)
admin.site.register(Signatories, SignatoriesAdmin)