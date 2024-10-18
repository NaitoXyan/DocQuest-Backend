from django.contrib import admin
from django.urls import re_path, include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # create role
    path('create_role', views.create_role),

    re_path('signup', views.signup),
    re_path('name_and_roles', views.name_and_roles),
    re_path('create_project', views.create_project),

    # edit user profile
    re_path('get_user_details', views.user_profile),
    path('edit_user_details/<int:pk>/', views.edit_profile),

    # create project
    path('create_project', views.create_project),

    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    # get project
    path('get_project/<int:pk>/', views.get_project),
    path('get_project_status/<int:pk>/', views.get_project_status),

    # get address
    path('get_regions', views.get_regions),
    path('get_provinces/<int:regionID>/', views.get_provinces),
    path('get_cities/<int:provinceID>/', views.get_cities),
    path('get_barangays/<int:cityID>/', views.get_barangays),

    re_path('test_token', views.test_token),
]

# /auth/users/ Register a new user

# log in
# /auth/token/login/

# access user’s details
# /auth/users/me/

# log out
# /auth/token/logout/