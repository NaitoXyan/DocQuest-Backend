from django.contrib import admin
from django.urls import re_path, include
from . import views

urlpatterns = [
    re_path('admin/', admin.site.urls),

    re_path('signup', views.signup),
    re_path('name_and_roles', views.name_and_roles),
    re_path('roles', views.roles),
    re_path('create_project', views.create_project),
    re_path('test_token', views.test_token),

    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]

# /auth/users/ Register a new user

# log in
# /auth/token/login/

# access user’s details
# /auth/users/me/

# log out
# /auth/token/logout/