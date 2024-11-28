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
    path('get_programCategory', views.get_programCategory),
    path('get_projectCategory', views.get_projectCategory),
    path('get_campuses', views.get_campuses),
    path('get_colleges/', views.get_colleges),
    path('get_programs/', views.get_programs),
    path('get_checklist', views.get_checklist),
    path('create_deliverables', views.create_deliverables),
    path('college/<int:pk>/dean/', views.get_college_dean),
    path('program/<int:pk>/chair/', views.get_program_chair),

    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    # get project
    path('get_project/<int:pk>/', views.get_project),
    path('get_project_status/<int:pk>/', views.get_project_status),

    # get mga i review
    path('get_projects_to_review', views.get_projects_to_review),

    #mag review
    path('review_project', views.review_project),

    # update signatory sa project
    # path('update_signatory_status/<int:signatory_id>/', views.update_signatory_status),

    #send notification
    path('send_notifications_to_director_and_staff', views.send_notifications_to_director_and_staff),

    #review post request
    path('create_review', views.create_review),

    # director get reviews
    path('get_review', views.get_review),

    #Director approve or deny project
    path('approve_or_deny_project/<int:review_id>/', views.approve_or_deny_project),

    # Director approve or deny MOA
    path('approve_or_deny_moa/<int:review_id>/', views.approve_or_deny_moa),

    #edit project
    path('edit_project/<int:project_id>/', views.edit_project),

    # get project review 
    path('get_project_review/<int:projectID>/', views.get_project_review),

    # post moa
    path('create_moa', views.create_moa),

    # get moa
    path('get_moa_status/<int:pk>/', views.get_moa_status),

    # get specific moa
    path('get_moa/<int:pk>/', views.get_specific_moa),

    # edit moa
    path('edit_moa/<int:moa_id>/', views.edit_moa),

    # submit pdf
    path('create_document_pdf', views.create_document_pdf),

    # get all proponents name
    path('get_users_exclude_roles', views.get_users_exclude_roles),

    # get/create agency
    path('create_agency', views.create_agency),
    path('get_agencies', views.get_agencies),

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