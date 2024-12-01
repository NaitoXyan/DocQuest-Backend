from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

# signup
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Save user through serializer
                user = serializer.save()
                
                # Set password separately as per existing view
                user.set_password(request.data['password'])
                user.save()

                return Response(
                    {"message": "User created and role assigned"},
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def coordinator_create_user(request):
    try:
        with transaction.atomic():
            # Extract user data from the request
            email = request.data.get('email')
            password = request.data.get('password')
            firstname = request.data.get('firstname')
            middlename = request.data.get('middlename', "")
            lastname = request.data.get('lastname')
            contact_number = request.data.get('contactNumber', "NO NUMBER")
            role_ids = request.data.get('role', [])  # Expecting a list of role IDs
            college_id = request.data.get('college')  # College ID
            program_id = request.data.get('program')  # Program ID
            is_staff = request.data.get('is_staff', False)
            is_superuser = request.data.get('is_superuser', False)
            is_active = request.data.get('is_active', True)
            
            # Step 1: Validate email and password
            if not email:
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Step 2: Check for unique role constraint
            unique_role_code = "ecrd"
            unique_role = Roles.objects.filter(code=unique_role_code).first()
            if unique_role and unique_role.roleID in role_ids:
                if CustomUser.objects.filter(role=unique_role).exists():
                    return Response(
                        {"error": f"The role '{unique_role_code}' is already assigned to another user."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Step 3: Create the user instance
            try:
                user = CustomUser(
                    email=email,
                    firstname=firstname,
                    middlename=middlename,
                    lastname=lastname,
                    contactNumber=contact_number,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    is_active=is_active,
                )
                user.set_password(password)  # Hash the password
                user.save()  # Save the user
            except Exception as e:
                return Response({"error": f"Error creating user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Step 4: Assign roles
            try:
                roles = Roles.objects.filter(roleID__in=role_ids)
                user.role.set(roles)
            except Exception as e:
                return Response({"error": f"Error assigning roles: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Step 5: Handle faculty information
            try:
                if college_id or program_id:
                    college = College.objects.filter(collegeID=college_id).first()
                    program = Program.objects.filter(programID=program_id).first()
                    if college_id and not college:
                        return Response({"error": "Invalid college ID provided."}, status=status.HTTP_400_BAD_REQUEST)
                    if program_id and not program:
                        return Response({"error": "Invalid program ID provided."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    Faculty.objects.update_or_create(
                        userID=user,
                        defaults={
                            'collegeID': college,
                            'programID': program,
                        }
                    )
            except Exception as e:
                return Response({"error": f"Error updating faculty information: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({"message": "User created successfully.", "userID": user.userID}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# inig login mag fetch user name and roles
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def name_and_roles(request):
    user = request.user  # Get the authenticated user from the request

    # Serialize user data
    user_serializer = UserLoginSerializer(instance=user)

    # Return combined response with user data and roles
    return Response({
        "userID": user_serializer.data['userID'],
        "firstname": user_serializer.data['firstname'],
        "lastname": user_serializer.data['lastname'],
        "roles": user_serializer.data['roles']
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user  # Get the authenticated user from the request

    # Serialize user data
    user_serializer = UserEditProfileSerializer(instance=user)

    # Return combined response with user data and roles
    return Response(user_serializer.data)

# edit user profile
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_profile(request, pk):
    try:
        instance = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

    # Use partial updates via serializer
    serializer = UserEditProfileSerializer(instance, data=request.data, partial=True)

    if serializer.is_valid():
        # Check if the password field is in the request
        if 'password' in request.data:
            password = request.data['password']
            instance.set_password(password)  # Hash and save the password
            instance.save()
        else:
            serializer.save()  # Save other fields without password processing

        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_role(request):
    role_serializer = RoleSerializer(data=request.data)

    if role_serializer.is_valid():
        role_serializer.save()
        return Response({"message": "Role successfuly created"}, status=status.HTTP_201_CREATED)

    return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_review(request):
    user = request.user

    # Fetch reviews with related content type
    eligible_reviews = Review.objects.filter(
        reviewedByID=user,
        sequence__gt=0
    ).select_related('content_type')

    # Filter for project reviews and sort by sequence
    project_reviews = []
    for review in eligible_reviews:
        # Check if the source is a Project using content_type
        if review.content_type.model == 'project':
            try:
                project = Project.objects.filter(projectID=review.source_id).first()
                
                if not project:
                    continue  # Skip if no project found
                
                # Previous review check logic
                previous_reviews = Review.objects.filter(
                    source_id=review.source_id,
                    sequence__lt=review.sequence,
                )

                # Check if all previous reviews are approved
                if previous_reviews.exists():
                    all_approved = all(r.reviewStatus == 'approved' for r in previous_reviews)
                else:
                    # If no previous reviews, it means the first review, so it's automatically available
                    all_approved = True

                # Add the review to the list only if all prior reviews are approved
                if all_approved:
                    review.source = project  # Attach project details to the review
                    project_reviews.append(review)

            except Project.DoesNotExist:
                continue  # Skip if project does not exist

    # Serialize the filtered reviews
    serializer = ProjectReviewSerializer(project_reviews, many=True)
    return Response({"reviews": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_project(request):
    try:
        review_id = request.data.get('reviewID')
        action = request.data.get('action')  # 'approve' or 'deny'
        comment = request.data.get('comment', '')  # Optional comment

        # Validate input
        if action not in ['approve', 'deny']:
            return Response({"error": "Invalid action specified"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the review
        review = Review.objects.get(reviewID=review_id, reviewedByID=request.user)

        # Update review status
        if action == 'approve':
            review.reviewStatus = 'approved'
        elif action == 'deny':
            review.reviewStatus = 'rejected'

        review.comment = comment
        review.save()

        # Handle project status based on review action
        project = review.source  # Assuming 'source' is a ForeignKey to Project model

        # Assuming the role code for the director is 'director'
        if action == 'approve':
            # Check if the reviewer is a director (based on role code)
            user_roles = request.user.role.all()
            if 'ecrd' in [role.code for role in user_roles]:
                project.status = 'approved'
                project.save()

            # Check if all reviews in the current sequence are approved
            current_sequence_reviews = Review.objects.filter(
                source_id=review.source_id,
                content_type=review.content_type,
                sequence=review.sequence
            )
            if all(r.reviewStatus == 'approved' for r in current_sequence_reviews):
                # Activate the next sequence of reviews
                next_sequence_reviews = Review.objects.filter(
                    source_id=review.source_id,
                    content_type=review.content_type,
                    sequence=review.sequence + 1,
                    reviewStatus='pending'
                )
                next_sequence_reviews.update(reviewStatus='pending')

                # Notify the next reviewers
                for next_review in next_sequence_reviews:
                    Notification.objects.create(
                        userID=next_review.reviewedByID,
                        content_type=next_review.content_type,
                        source_id=next_review.source_id,
                        message='A project is ready for your review.'
                    )

        elif action == 'deny':
            # Set the project status to 'rejected'
            project.status = 'rejected'
            project.save()

            Notification.objects.create(
                        userID=review.contentOwnerID,
                        content_type=review.content_type,
                        source_id=review.source_id,
                        message='Your project has been rejected.'
                    )

        return Response({"message": f"Review successfully {action}ed."}, status=status.HTTP_200_OK)

    except Review.DoesNotExist:
        return Response({"error": "Review not found or not assigned to you"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    serializer = PostProjectSerializer(data=request.data)

    if serializer.is_valid():
        # Create project
        project = serializer.save()

        if project.dateCreated and not project.uniqueCode:
            project.uniqueCode = f"{project.projectID}-{project.dateCreated.strftime('%Y%m%d')}"
        project.save()

        # Create deliverables
        deliverable_ids = request.data.get('deliverables', [])
        deliverables_data = [
            {
                'userID': request.user.userID,
                'projectID': project.projectID,
                'deliverableID': deliverable_id
            }
            for deliverable_id in deliverable_ids
        ]

        deliverables_serializer = UserProjectDeliverablesSerializer(
            data=deliverables_data, 
            many=True
        )
        
        if deliverables_serializer.is_valid():
            deliverables_serializer.save()
        else:
            project.delete()
            return Response(
                deliverables_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create reviews for all colleges and approvers
        try:
            content_type = ContentType.objects.get(model='project')
            colleges = request.data.get('approvers', [])

            review_data = []
            sequence_counter = 1

            for college in colleges:
                collegeID = college.get('collegeID')
                program_chair_ids = college.get('programChairs', [])
                dean_id = college.get('collegeDean')

                # Add reviews for program chairs (same sequence)
                for chair_id in program_chair_ids:
                    review_data.append({
                        'contentOwnerID': request.user.userID,
                        'content_type': content_type.id,
                        'source_id': project.projectID,
                        'reviewedByID': chair_id,
                        'collegeID': collegeID,
                        'reviewStatus': 'pending',
                        'sequence': sequence_counter,  # Sequence for program chairs
                    })

                # Add review for college dean (next sequence after chairs)
                review_data.append({
                    'contentOwnerID': request.user.userID,
                    'content_type': content_type.id,
                    'source_id': project.projectID,
                    'reviewedByID': dean_id,
                    'collegeID': collegeID,
                    'reviewStatus': 'pending',
                    'sequence': sequence_counter + 1,  # Sequence for dean after chairs
                })

                sequence_counter += 2  # Increment sequence for the next college

            # Add director as the last reviewer
            director = CustomUser.objects.filter(
                role__code='ecrd'
            ).first()  # There's only one director

            if director:
                review_data.append({
                    'contentOwnerID': request.user.userID,
                    'content_type': content_type.id,
                    'source_id': project.projectID,
                    'reviewedByID': director.userID,
                    'collegeID': None,  # Director is not tied to a specific college
                    'reviewStatus': 'pending',
                    'sequence': sequence_counter,  # Last sequence in the review workflow
                })

            review_serializer = ReviewSerializer(data=review_data, many=True)
            if review_serializer.is_valid():
                review_serializer.save()
            else:
                project.delete()
                return Response(
                    review_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ContentType.DoesNotExist:
            project.delete()
            return Response(
                {"error": "Invalid content type specified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create notifications for the first reviewer in the sequence
        try:
            # Identify the first reviewer for the project
            first_review = Review.objects.filter(
                source_id=project.projectID, 
                sequence=1,  # First sequence in the review workflow
                reviewStatus='pending'  # Ensure it targets pending reviews
            ).first()

            if first_review:
                # Notify the first reviewer
                Notification.objects.create(
                    userID=first_review.reviewedByID,
                    content_type=content_type,
                    source_id=project.projectID,
                    message='A new project is awaiting your review.'
                )
            else:
                # Fallback: Notify admin/staff if no first reviewer found
                director_staff_users = CustomUser.objects.filter(
                    role__code__in=['ecrd', 'estf']
                ).distinct()

                notifications = [
                    Notification(
                        userID=user,
                        content_type=content_type,
                        source_id=project.projectID,
                        message='No reviewers found for the project. Please assign one.'
                    )
                    for user in director_staff_users
                ]
                Notification.objects.bulk_create(notifications)

        except Exception as e:
            project.delete()
            return Response(
                {"error": f"Error creating notifications: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "Project successfully created with deliverables, review, and notifications",
            "projectID": project.projectID
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, pk): 
    user = request.user  # Get the authenticated user

    # Try to fetch the project by its ID
    try:
        project = Project.objects.get(pk=pk)  # Use pk to fetch the project directly
    except Project.DoesNotExist:
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    project_serializer = GetProjectSerializer(instance=project)
    return Response(project_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_checklist(request):
    # Query all regions
    deliverables = Deliverables.objects.all()

    # Serialize the regions
    serializer = DeliverablesSerializer(deliverables, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_deliverables(request):
    serializer = UserProjectDeliverablesSerializer(data=request.data)

    if serializer.is_valid():
        deliverables = serializer.save()
        return Response({"message": "Deliverables successfuly created"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notifications_to_director_and_staff(request):
    # Get content type and object ID from request data
    content_type_model = request.data.get('content_type')
    source_id = request.data.get('source_id')

    # Determine the message based on content type
    if content_type_model.lower() == 'project':
        message = 'New project to review'
    elif content_type_model.lower() == 'moa':
        message = 'New MOA to review'
    else:
        return Response(
            {"error": "Invalid content type specified. Must be 'project' or 'moa'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate if the content type exists in the ContentType table
    try:
        content_type = ContentType.objects.get(model=content_type_model.lower())
    except ContentType.DoesNotExist:
        return Response(
            {"error": "Invalid content type specified"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Filter users with roles 'director' or 'staff'
    director_staff_users = CustomUser.objects.filter(
        role__code__in=['ecrd', 'estf']
    ).distinct()

    # Create notifications for each user
    notifications = [
        Notification(
            userID=user,
            content_type=content_type,
            source_id=source_id,
            message=message
        )
        for user in director_staff_users
    ]

    # Bulk create notifications
    Notification.objects.bulk_create(notifications)

    # Serialize and return created notifications
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    # Get the logged-in user as content owner
    content_owner = request.user

    # Extract content type and source ID from request data
    content_type_model = request.data.get('content_type')
    source_id = request.data.get('source_id')
    comment = request.data.get('comment', '')

    # Validate and retrieve the content type
    try:
        content_type = ContentType.objects.get(model=content_type_model.lower())
    except ContentType.DoesNotExist:
        return Response(
            {"error": "Invalid content type specified. Must be 'project' or 'moa'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find a user with the 'director' role to assign as reviewedBy
    try:
        director_user = CustomUser.objects.filter(role__code='ecrd').first()
        if not director_user:
            return Response(
                {"error": "No user with the 'director' role found."},
                status=status.HTTP_404_NOT_FOUND
            )
    except CustomUser.DoesNotExist:
        return Response(
            {"error": "Error retrieving director user."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create the review instance
    review_data = {
        'contentOwnerID': content_owner.userID,
        'content_type': content_type.id,
        'source_id': source_id,
        'reviewedByID': director_user.userID,
        'comment': comment,
        'reviewStatus': 'pending'
    }
    
    serializer = ReviewSerializer(data=review_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_or_deny_project(request, review_id):
    # List of roles that can approve/deny projects
    AUTHORIZED_ROLES = ['prch', 'cldn', 'ecrd']
    
    # Check if user has any of the authorized roles
    if not request.user.role.filter(code__in=AUTHORIZED_ROLES).exists():
        return Response(
            {"error": "You do not have the required permissions to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Fetch the review instance
        review = Review.objects.get(reviewID=review_id)
        project = Project.objects.get(projectID=review.source_id)

        # Get the user's role code
        user_role = request.user.role.first().code

        # Determine approval or rejection
        action = request.data.get('action')
        comment = request.data.get('comment', '')

        # Initialize notification variables
        notification_user = None
        message = ''

        if action == 'approve':
            review.comment = comment
            # Increment approval counter
            review.approvalCounter += 1
            project.approvalCounter += 1
            
            # Determine notification recipient and message based on approval counter
            if review.approvalCounter == 1:
                review.reviewedByID = request.user
                review.reviewerResponsible = 'prch'
                # Notify CLDN role user after first approval (from PRCH)
                notification_user = CustomUser.objects.filter(role__code='cldn').first()
                message = f'Project "{project.projectTitle}" requires your review and approval'
                project.status = 'pending'
            
            elif review.approvalCounter == 2:
                review.reviewedByID = request.user
                review.reviewerResponsible = 'cldn'
                # Notify ECRD role user after second approval (from CLDN)
                notification_user = CustomUser.objects.filter(role__code='ecrd').first()
                message = f'Project "{project.projectTitle}" requires your final review and approval'
                project.status = 'pending'
            
            elif review.approvalCounter >= 3:
                review.reviewedByID = request.user
                review.reviewerResponsible = 'ecrd'
                # Notify content owner after final approval (from ECRD)
                notification_user = review.contentOwnerID
                message = f'Your project "{project.projectTitle}" has been fully approved and is ready to print'
                project.status = 'approved'
                review.reviewStatus = 'approved'
                
        elif action == 'deny':
            review.reviewStatus = 'rejected'
            review.comment = comment
            review.approvalCounter = 0  # Reset counter on rejection
            project.approvalCounter = 0
            project.status = 'rejected'
            review.reviewedByID = request.user
            review.reviewerResponsible = user_role
            notification_user = review.contentOwnerID
            message = f'Your project "{project.projectTitle}" has been rejected. Reason: {comment}'
        else:
            return Response(
                {"error": "Invalid action. Must be 'approve' or 'deny'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save changes to the review and project
        review.save()
        project.save()

        # Create notification for the appropriate user
        if notification_user:
            notification = Notification.objects.create(
                userID=notification_user,
                content_type=ContentType.objects.get_for_model(Review),
                source_id=review.reviewID,
                message=message,
                status='Unread'
            )
            notification_serializer = NotificationSerializer(notification)
        else:
            notification_serializer = None

        # Serialize and return the updated review and notification
        review_serializer = ReviewSerializer(review)
        
        response_data = {
            "review": review_serializer.data,
            "project_status": project.status,
            "approval_counter": review.approvalCounter
        }

        if notification_serializer:
            response_data["notification"] = notification_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)

    except Review.DoesNotExist:
        return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response(
            {"error": "Could not find appropriate user to notify."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_or_deny_moa(request, review_id):
    # List of roles that can approve/deny MOAs
    AUTHORIZED_ROLES = ['vpala', 'ecrd']
    
    # Check if user has any of the authorized roles
    if not request.user.role.filter(code__in=AUTHORIZED_ROLES).exists():
        return Response(
            {"error": "You do not have the required permissions to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Fetch the review instance
        review = Review.objects.get(reviewID=review_id)
        moa = MOA.objects.get(moaID=review.source_id)

        # Get the user's role code
        user_role = request.user.role.first().code

        # Determine approval or rejection
        action = request.data.get('action')
        comment = request.data.get('comment', '')

        # Initialize notification variables
        notification_user = None
        message = ''

        if action == 'approve':
            review.comment = comment
            # Increment approval counter
            review.approvalCounter += 1
            moa.approvalCounter += 1
            
            # Determine notification recipient and message based on approval counter
            if review.approvalCounter == 1:
                review.reviewedByID = request.user
                review.reviewerResponsible = 'vpala'
                # Notify ECRD role user after first approval (from VPALA)
                notification_user = CustomUser.objects.filter(role__code='ecrd').first()
                message = f'MOA requires your final review and approval'
                moa.status = 'pending'
            
            elif review.approvalCounter >= 2:
                review.reviewedByID = request.user
                review.reviewerResponsible = 'ecrd'
                # After ECRD approval, notify staff users
                moa.status = 'approved'
                review.reviewStatus= 'approved'
                # First notify content owner
                notification_user = review.contentOwnerID
                message = f'Your MOA has been fully approved'
                
                # Then create notifications for all staff users
                staff_users = CustomUser.objects.filter(role__code='estf')
                for staff in staff_users:
                    Notification.objects.create(
                        userID=staff,
                        content_type=ContentType.objects.get_for_model(MOA),
                        source_id=moa.moaID,
                        message=f'New MOA has been approved and ready for implementation',
                        status='Unread'
                    )
                
        elif action == 'deny':
            review.reviewStatus = 'rejected'
            review.comment = comment
            review.approvalCounter = 0  # Reset counter on rejection
            moa.approvalCounter = 0
            moa.status = 'rejected'
            review.reviewedByID = request.user
            review.reviewerResponsible = user_role
            notification_user = review.contentOwnerID
            message = f'Your MOA has been rejected. Reason: {comment}'
        else:
            return Response(
                {"error": "Invalid action. Must be 'approve' or 'deny'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save changes to the review and MOA
        review.save()
        moa.save()

        # Create notification for the appropriate user
        if notification_user:
            notification = Notification.objects.create(
                userID=notification_user,
                content_type=ContentType.objects.get_for_model(Review),
                source_id=review.reviewID,
                message=message,
                status='Unread'
            )
            notification_serializer = NotificationSerializer(notification)
        else:
            notification_serializer = None

        # Serialize and return the updated review and notification
        review_serializer = ReviewSerializer(review)
        
        response_data = {
            "review": review_serializer.data,
            "moa_status": moa.status,
            "approval_counter": review.approvalCounter
        }

        if notification_serializer:
            response_data["notification"] = notification_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)

    except Review.DoesNotExist:
        return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
    except MOA.DoesNotExist:
        return Response({"error": "MOA not found."}, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response(
            {"error": "Could not find appropriate user to notify."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_project(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateProjectSerializer(instance=project, data=request.data, partial=True)
    if serializer.is_valid():
        project = serializer.save()

        # Update related many-to-many or reverse relationships
        if 'agency' in request.data:
            project.agency.set(request.data['agency'])

        if 'proponents' in request.data:
            project.proponents.set(request.data['proponents'])

        # Get all users with the 'Director' role code
        reviewer_role_code = 'prch'  # Assuming 'DIR' is the code for the Director role
        reviewer_users = CustomUser.objects.filter(role__code=reviewer_role_code)

        # Send notification to each director
        for director in reviewer_users:
            Notification.objects.create(
                userID=director,
                content_type=ContentType.objects.get_for_model(Project),
                source_id=project.projectID,
                message="Project has been updated and requires review."
            )

        # Assign a director as the reviewer (assuming one director for the review)
        if reviewer_users.exists():
            review = Review.objects.create(
                contentOwnerID=request.user,
                content_type=ContentType.objects.get_for_model(Project),
                source_id=project.projectID,
                reviewedByID=reviewer_users.first(),  # Assigning the first director found
                reviewStatus='pending',
                comment="Project has been edited and is pending approval."
            )

        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_moa(request):
    # Create a mutable copy of request.data
    data = request.data.copy()
    
    # Assign the authenticated user as userID
    data['userID'] = request.user.userID

    serializer = PostMOASerializer(data=data)

    if serializer.is_valid():
        # Save the MOA
        moa = serializer.save(userID=request.user)

        # Generate unique code if not already present
        if moa.dateCreated and not moa.uniqueCode:
            moa.uniqueCode = f"{moa.moaID}-{moa.dateCreated.strftime('%Y%m%d')}"
        moa.save()

        # Link the MOA to the specified Project (if applicable)
        project_id = data.get('projectID')
        if project_id:
            try:
                project = Project.objects.get(projectID=project_id)
                project.moaID = moa
                project.save()
            except Project.DoesNotExist:
                return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        # Find the Director with 'ecrd' role code for initial review
        try:
            director = CustomUser.objects.get(role__code='ecrd')
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "No Director found for review."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create initial review by Director
        initial_review = Review.objects.create(
            contentOwnerID=request.user,
            content_type=ContentType.objects.get_for_model(MOA),
            source_id=moa.moaID,
            reviewedByID=director,
            reviewStatus='pending',
            reviewerResponsible='director'  # Explicitly mark as director's review
        )

        # Create Director Notification
        Notification.objects.create(
            userID=director,
            content_type=ContentType.objects.get_for_model(MOA),
            source_id=moa.moaID,
            message="New MOA requires your initial review."
        )

        return Response({
            "message": "MOA submitted for initial director review.",
            "moaID": moa.moaID,
            "uniqueCode": moa.uniqueCode
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_moa_reviews(request):
    # Determine the user's role
    user_roles = request.user.role.values_list('code', flat=True)
    
    # Prepare the base query for reviews
    reviews = Review.objects.filter(
        content_type=ContentType.objects.get_for_model(MOA),
        reviewStatus='pending'
    )
    
    # Filter reviews based on user's role
    if 'ecrd' in user_roles:
        # Director can see MOAs pending director review
        reviews = reviews.filter(
            reviewedByID=request.user, 
            reviewerResponsible='director'
        )
    elif 'vpala' in user_roles:
        # VPALA can see MOAs pending final review
        reviews = reviews.filter(
            reviewedByID=request.user, 
            reviewerResponsible='vpala'
        )
    else:
        # If user doesn't have review roles, return empty result
        return Response([], status=status.HTTP_200_OK)
    
    # Prepare response data
    review_data = []
    for review in reviews:
        moa = review.source
        
        # Try to find associated project
        try:
            project = Project.objects.get(moaID=moa)
            project_info = {
                'projectID': project.projectID,
                'projectTitle': project.projectTitle
            }
        except Project.DoesNotExist:
            project_info = None
        
        review_data.append({
            'moaID': moa.moaID,
            'status': moa.status,
            'project': project_info,
            'reviewID': review.reviewID,
            'reviewStatus': review.reviewStatus,
            'reviewerResponsible': review.reviewerResponsible
        })
    
    return Response(review_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def director_review_moa(request, moa_id):
    try:
        # Verify the user is the Director
        if not request.user.role.filter(code='ecrd').exists():
            return Response(
                {"error": "Unauthorized. Only Director can perform this review."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Find the MOA and its pending review
        moa = MOA.objects.get(moaID=moa_id)
        review = Review.objects.get(
            source_id=moa_id, 
            content_type=ContentType.objects.get_for_model(MOA),
            reviewerResponsible='director',
            reviewStatus='pending'
        )

        # Get review decision from request
        decision = request.data.get('decision')  # 'approved' or 'rejected'
        comment = request.data.get('comment', '')

        # Update review
        review.reviewStatus = decision
        review.comment = comment
        review.reviewDate = timezone.now()
        review.save()

        # If approved, prepare for VPALA review
        if decision == 'approved':
            # Find VPALA user
            try:
                vpala = CustomUser.objects.get(role__code='vpala')
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "No VPALA found for final review."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create VPALA review
            vpala_review = Review.objects.create(
                contentOwnerID=moa.userID,
                content_type=ContentType.objects.get_for_model(MOA),
                source_id=moa.moaID,
                reviewedByID=vpala,
                reviewStatus='pending',
                reviewerResponsible='vpala'
            )

            # Create VPALA Notification
            Notification.objects.create(
                userID=vpala,
                content_type=ContentType.objects.get_for_model(MOA),
                source_id=moa.moaID,
                message="MOA has passed initial review and requires final approval."
            )

            return Response({
                "message": "MOA approved by Director and sent to VPALA for final review.",
                "status": "director_approved"
            }, status=status.HTTP_200_OK)
        else:
            # If rejected, update MOA status
            moa.status = 'rejected'
            moa.save()

            # Notify original user about rejection
            Notification.objects.create(
                userID=moa.userID,
                content_type=ContentType.objects.get_for_model(MOA),
                source_id=moa.moaID,
                message="Your MOA has been rejected during initial review."
            )

            return Response({
                "message": "MOA rejected by Director.",
                "status": "director_rejected"
            }, status=status.HTTP_200_OK)

    except MOA.DoesNotExist:
        return Response(
            {"error": "MOA not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Review.DoesNotExist:
        return Response(
            {"error": "No pending review found for this MOA."}, 
            status=status.HTTP_404_NOT_FOUND
        )

# Similar view can be created for VPALA final approval
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vpala_final_review_moa(request, moa_id):
    try:
        # Verify the user is the VPALA
        if not request.user.role.filter(code='vpala').exists():
            return Response(
                {"error": "Unauthorized. Only VPALA can perform final review."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Find the MOA and its pending VPALA review
        moa = MOA.objects.get(moaID=moa_id)
        review = Review.objects.get(
            source_id=moa_id, 
            content_type=ContentType.objects.get_for_model(MOA),
            reviewerResponsible='vpala',
            reviewStatus='pending'
        )

        # Get review decision from request
        decision = request.data.get('decision')  # 'approved' or 'rejected'
        comment = request.data.get('comment', '')

        # Update review
        review.reviewStatus = decision
        review.comment = comment
        review.reviewDate = timezone.now()
        review.save()

        # Update MOA status based on final decision
        if decision == 'approved':
            moa.status = 'approved'
            moa.save()

            # Notify original user about final approval
            Notification.objects.create(
                userID=moa.userID,
                content_type=ContentType.objects.get_for_model(MOA),
                source_id=moa.moaID,
                message="Your MOA has been fully approved."
            )

            return Response({
                "message": "MOA fully approved by VPALA.",
                "status": "final_approved"
            }, status=status.HTTP_200_OK)
        else:
            moa.status = 'rejected'
            moa.save()

            # Notify original user about final rejection
            Notification.objects.create(
                userID=moa.userID,
                content_type=ContentType.objects.get_for_model(MOA),
                source_id=moa.moaID,
                message="Your MOA has been rejected during final review."
            )

            return Response({
                "message": "MOA rejected during final review.",
                "status": "final_rejected"
            }, status=status.HTTP_200_OK)

    except MOA.DoesNotExist:
        return Response(
            {"error": "MOA not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Review.DoesNotExist:
        return Response(
            {"error": "No pending review found for this MOA."}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_moa(request, moa_id):
    try:
        moa = MOA.objects.get(pk=moa_id)
    except MOA.DoesNotExist:
        return Response({"error": "MOA not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateMOASerializer(instance=moa, data=request.data)
    if serializer.is_valid():
        # Reset MOA status to pending when edited
        moa.status = 'pending'
        moa = serializer.save()

        # Find the Director with 'ecrd' role code for review
        try:
            director = CustomUser.objects.get(role__code='ecrd')
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "No Director found for review."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new review for the edited MOA
        review = Review.objects.create(
            contentOwnerID=request.user,
            content_type=ContentType.objects.get_for_model(MOA),
            source_id=moa.moaID,
            reviewedByID=director,
            reviewStatus='pending',
            reviewerResponsible='director',
            comment="MOA has been edited and is pending re-approval."
        )

        # Create notification for the Director
        Notification.objects.create(
            userID=director,
            content_type=ContentType.objects.get_for_model(MOA),
            source_id=moa.moaID,
            message="MOA has been updated and requires review."
        )

        return Response({
            "message": "MOA updated and sent for review",
            "moaID": moa.moaID,
            "status": moa.status
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_document_pdf(request):
    serializer = DocumentPDFSerializer(data=request.data)
    if serializer.is_valid():
        document = serializer.save()

        # Determine the message and target user based on content type
        content_type = serializer.validated_data['content_type']
        source_id = serializer.validated_data['source_id']

        if content_type.model == 'project':
            # Retrieve the related Project instance
            try:
                project = Project.objects.get(pk=source_id)
                target_user = project.userID  # The user associated with the Project
                message = "Project is approved/complete signatures, prepare and submit MOA."
            except Project.DoesNotExist:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif content_type.model == 'moa':
            # Retrieve the related MOA instance
            try:
                moa = MOA.objects.get(pk=source_id)
                target_user = moa.userID  # The user associated with the MOA
                message = "MOA is approved, you can now start the project."
            except MOA.DoesNotExist:
                return Response({"error": "MOA not found"}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({"error": "Invalid content type"}, status=status.HTTP_400_BAD_REQUEST)

       # Create a notification for the target user
        Notification.objects.create(
            user=target_user,
            message=message,
            timestamp=document.timestamp
        )

        return Response({"message": message}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def update_signatory_status(request, signatory_id):
#     try:
#         # Fetch the Signatories instance by ID
#         signatory = Signatories.objects.get(pk=signatory_id)
#     except Signatories.DoesNotExist:
#         return Response({"error": "Signatory not found."}, status=status.HTTP_404_NOT_FOUND)

#     # Get the new approval status from the request data
#     new_status = request.data.get('approvalStatus')

#     if new_status not in dict(Signatories.APPROVAL_CHOICES).keys():
#         return Response({"error": "Invalid approval status."}, status=status.HTTP_400_BAD_REQUEST)

#     # Update the approval status
#     signatory.approvalStatus = new_status
    
#     # If the new status is approved, generate the signature code
#     if new_status == 'approved':
#         signatory.signatureCode = signatory.generate_signature_code()

#     # Save the updated signatory instance
#     signatory.save()

#     return Response({"message": "Approval status updated successfully.", "signatureCode": signatory.signatureCode}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_users_exclude_roles(request):
    # Filter users excluding those with role code "ecrd" or "estf"
    users = CustomUser.objects.exclude(role__code__in=["ecrd", "estf", "vpala"]).distinct()
    serializer = GetProponentsSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_agencies(request):
    agency = PartnerAgency.objects.all()

    agency_serializer = PartnerAgencySerializer(agency, many=True)

    return Response(agency_serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_agency(request):
    agency_serializer = PartnerAgencySerializer(data=request.data)

    if agency_serializer.is_valid():
        agency_serializer.save()
        return Response(agency_serializer.data, status=status.HTTP_201_CREATED)

    return Response(agency_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_regions(request):
    # Query all regions
    regions = Region.objects.all()

    # Serialize the regions
    region_serializer = RegionSerializer(regions, many=True)

    return Response(region_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_provinces(request, regionID):
    
    try:
        region = Region.objects.get(pk=regionID)
    except Region.DoesNotExist:
        return Response({"detail": "Region not found."}, status=status.HTTP_404_NOT_FOUND)
    
    provinces = Province.objects.filter(regionID=region)

    provinces_serializer = GetProvinceSerializer(provinces, many=True)

    return Response(provinces_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request, provinceID):

    try:
        province = Province.objects.get(pk=provinceID)
    except Province.DoesNotExist:
        return Response({"detail": "Province not found."}, status=status.HTTP_404_NOT_FOUND)

    cities = City.objects.filter(provinceID=province)

    cities_serializer = GetCitySerializer(cities, many=True)

    return Response(cities_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_barangays(request, cityID):

    try:
        city = City.objects.get(pk=cityID)
    except City.DoesNotExist:
        return Response({"detail": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    barangays = Barangay.objects.filter(cityID=city)

    barangays_serializer = GetBarangaySerializer(barangays, many=True)

    return Response(barangays_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_programCategory(request):
    programCategory = ProgramCategory.objects.all()
    serializer = ProgramCategorySerializer(programCategory, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_projectCategory(request):
    projectCategory = ProjectCategory.objects.all()
    serializer = ProjectCategorySerializer(projectCategory, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_campuses(request):
    # Query all regions
    campus = Campus.objects.all()

    # Serialize the regions
    campus_serializer = CampusSerializer(campus, many=True)

    return Response(campus_serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_colleges(request):
    """
    Fetch programs for multiple colleges.
    Expects a POST request with a JSON body containing 'collegeIDs': [list of college IDs].
    """
    campus_ids = request.data.get('campusIDs', [])
    
    if not isinstance(campus_ids, list) or not all(isinstance(id, int) for id in campus_ids):
        return Response(
            {"detail": "Invalid input. 'campusIDs' should be a list of integers."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Retrieve programs for the given colleges
    college = College.objects.filter(campusID__in=campus_ids)
    college_serializer = CollegeSerializer(college, many=True)

    return Response(college_serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_programs(request):
    """
    Fetch programs for multiple colleges.
    Expects a POST request with a JSON body containing 'collegeIDs': [list of college IDs].
    """
    college_ids = request.data.get('collegeIDs', [])
    
    if not isinstance(college_ids, list) or not all(isinstance(id, int) for id in college_ids):
        return Response(
            {"detail": "Invalid input. 'collegeIDs' should be a list of integers."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Retrieve programs for the given colleges
    programs = Program.objects.filter(collegeID__in=college_ids)
    programs_serializer = ProgramSerializer(programs, many=True)

    return Response(programs_serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_project_status(request, pk):
    # Get all projects for the user with userID equal to pk
    projects = Project.objects.filter(userID=pk)

    # Serialize the project data
    serializer = GetProjectStatusSerializer(projects, many=True)

    # Return the serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_moa_status(request, pk):
    # Get all projects for the user with userID equal to pk
    moa = MOA.objects.filter(userID=pk)

    # Serialize the project data
    serializer = GetMoaSerializer(moa, many=True)

    # Return the serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_specific_moa(request, pk): 
    user = request.user  # Get the authenticated user

    # Try to fetch the project by its ID
    try:
        moa = MOA.objects.get(pk=pk)  # Use pk to fetch the project directly
    except MOA.DoesNotExist:
        return Response({"detail": "MOA not found."}, status=status.HTTP_404_NOT_FOUND)

    moa_serializer = GetSpecificMoaSerializer(instance=moa)
    return Response(moa_serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_review(request, projectID):
    user = request.user

    try: 
        review = Review.objects.get(source_id=projectID)
    except Review.DoesNotExist:
        return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
    
    review_serializer = ProjectReviewSerializer(instance=review)
    return Response(review_serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_review(request):
#     user = request.user
#     user_roles = user.role.all().values_list('code', flat=True)

#     # Initialize an empty Q object for OR conditions
#     review_conditions = Q()

#     ## Add conditions based on user roles
#     for role in user_roles:
#         if role == 'prch':
#             # PRCH sees reviews with counter = 0 and content_type_name = 'project'
#             review_conditions |= Q(approvalCounter=0, reviewStatus='pending', content_type__model='project')
#             review_conditions |= Q(approvalCounter__gt=0, reviewStatus='pending', content_type__model='project')
#             review_conditions |= Q(approvalCounter=3, reviewStatus='approved', content_type__model='project')
#             review_conditions |= Q(approvalCounter=0, reviewedByID=user, reviewStatus='rejected', content_type__model='project')
#         elif role == 'cldn':
#             # CLDN sees reviews with counter = 1 and content_type_name = 'project'
#             review_conditions |= Q(approvalCounter=1, reviewStatus='pending', content_type__model='project')  #pending iya pa review
#             review_conditions |= Q(approvalCounter__gt=1, reviewStatus='pending', content_type__model='project') #pending pero approved na ni cldn
#             review_conditions |= Q(approvalCounter=3, reviewStatus='approved', content_type__model='project') #approved nas tanan
#             review_conditions |= Q(approvalCounter=0, reviewedByID=user, reviewStatus='rejected', content_type__model='project')
#         elif role == 'vpala':
#             # VPALA sees reviews with content_type_name = 'moa'
#             review_conditions |= Q(approvalCounter=0, reviewStatus='pending', content_type__model='moa')
#             review_conditions |= Q(approvalCounter__gt=0, reviewStatus='pending', content_type__model='moa')
#             review_conditions |= Q(approvalCounter=2, reviewStatus='approved', content_type__model='moa')
#             review_conditions |= Q(approvalCounter=0, reviewedByID=user, reviewStatus='rejected', content_type__model='moa')
#         elif role == 'ecrd':
#             # ECRD sees all reviews
#             review_conditions |= Q(approvalCounter=2, reviewStatus='pending', content_type__model='project')
#             review_conditions |= Q(approvalCounter=1, reviewStatus='pending', content_type__model='moa')
#             review_conditions |= Q(approvalCounter=3, reviewStatus='approved', content_type__model='project')
#             review_conditions |= Q(approvalCounter=2, reviewStatus='approved', content_type__model='moa')
#             review_conditions |= Q(approvalCounter=0, reviewedByID=user, reviewStatus='rejected', content_type__model='project')
#             review_conditions |= Q(approvalCounter=0, reviewedByID=user, reviewStatus='rejected', content_type__model='moa')

#     # Get reviews based on the constructed conditions
#     reviews = Review.objects.filter(review_conditions).order_by('-reviewDate')

#     serializer = ProjectReviewSerializer(reviews, many=True)
#     return Response({
#         "reviews": serializer.data,
#         "user_roles": list(user_roles),  # Include user roles for debugging
#         "total_count": reviews.count()
#     }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_college_dean(request, pk):
    try:
        college = College.objects.get(pk=pk)
        serializer = GetCollegeDeanSerializer(college)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except College.DoesNotExist:
        return Response({"error": "College not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_program_chair(request, pk):
    try:
        program = Program.objects.get(pk=pk)
        serializer = GetProgramChairSerializer(program)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Program.DoesNotExist:
        return Response({"error": "Program not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reviews_with_projectID(request, pk):
    reviews = Review.objects.filter(source_id=pk)  # Filter by projectID (or adjust as needed)
    if reviews.exists():
        serializer = GetReviewsWithProjectIDSerializer(reviews, many=True)  # Use `many=True` for queryset
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "No reviews found for the given projectID"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_review(request, review_id):
    review = get_object_or_404(Review, reviewID=review_id)
    review.reviewStatus = 'approved'
    review.save()

    # Check if all reviews in the current sequence are approved
    pending_reviews = Review.objects.filter(
        sequence=review.sequence,
        collegeID=review.collegeID,
        reviewStatus='pending'
    )

    if not pending_reviews.exists():
        # Unlock the next sequence
        next_reviews = Review.objects.filter(
            sequence=review.sequence + 1,
            source_id=review.source_id
        )
        for next_review in next_reviews:
            next_review.reviewStatus = 'pending'
            next_review.save()

    return Response({"message": "Review approved successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_projects(request):
    # Query all projects from the database
    projects = Project.objects.all()

    # Serialize the projects using GetAllProjectsSerializer
    serializer = GetAllProjectsSerializer(projects, many=True)

    # Return the serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coordinator_get_roles(request):
    """
    Get roles with code 'rglr' or 'pjlr'.
    """
    roles = Roles.objects.filter(code__in=['rglr', 'pjlr'])
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def coordinator_edit_user_role(request):
    user_id = request.data.get('userID')
    role_ids = request.data.get('role')  # Expecting an array of role IDs

    if not user_id or not role_ids:
        return Response({"error": "userID and role fields are required."}, status=400)

    try:
        user = CustomUser.objects.get(userID=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

    try:
        # Use roleID instead of id for filtering
        roles = Roles.objects.filter(roleID__in=role_ids)
        if len(roles) != len(role_ids):
            return Response({"error": "One or more roles are invalid."}, status=400)
        
        # Update the user's roles
        user.role.set(roles)
        
        return Response({"message": "User roles updated successfully."}, status=200)
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_projects_of_program(request):
    user = request.user

    # Step 1: Fetch Faculty instance for the user
    try:
        faculty = Faculty.objects.get(userID=user)
    except Faculty.DoesNotExist:
        return Response({"error": "Faculty not found"}, status=404)

    # Step 2: Serialize programID
    program_serializer = GetProgramUsingFacultySerializer(faculty)
    program_id = program_serializer.data['programID']

    # Step 3: Query projects for the program
    projects = Project.objects.filter(program__programID=program_id)  # Adjust filter as per your model relationships

    # Step 4: Serialize the projects
    project_serializer = GetProjectsCountUsingProgram(projects, many=True)

    return Response(project_serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_by_program(request):
    # Get the logged-in user
    user = request.user

    # Check if the user has the "coord" role
    if not user.role.filter(code='coord').exists():
        raise PermissionDenied("You do not have permission to access this data.")
    
    # Get the current user's programID
    try:
        faculty = Faculty.objects.get(userID=user)
    except Faculty.DoesNotExist:
        return Response({"error": "User is not associated with a faculty."}, status=400)
    
    program_id = faculty.programID

    # Get all users with the same programID and role codes "rglr" or "pjlr"
    users = CustomUser.objects.filter(
        role__code__in=['rglr', 'pjlr'],
        faculty__programID=program_id,
        is_active = 1  
    ).distinct()

    # Serialize and return the data
    serializer = UsersByProgramSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_program_to_campus(request):
    user = request.user

    # Step 1: Fetch Faculty instance for the user
    try:
        faculty = Faculty.objects.get(userID=user)
    except Faculty.DoesNotExist:
        return Response({"error": "Faculty not found"}, status=404)

    # Step 2: Serialize programID
    program_serializer = CoordinatorProgramToCampus(faculty)

    return Response(program_serializer.data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))