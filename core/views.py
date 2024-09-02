from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.core.paginator import Paginator

from rest_framework.views import APIView

from core import models as core_models
from core import forms as core_forms
from core import serializers as core_serializers
from core import utils as core_utils 


class CreateUserProfile(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        data["email"] = data.get("email", "").lower()
        form = core_forms.UserProfileForm(data)
        
        if form.is_valid():
            if core_models.UserProfile.objects.filter(email=data["email"]).exists():
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Email already exists"
                )

            user_profile = form.save(commit=False)
            if data.get('password') == data.get('confirm_password'):
                user = core_models.User.objects.create_user(
                    username=user_profile.email,
                    first_name=user_profile.name.split()[0],
                    last_name=user_profile.name.split()[-1],
                    email=user_profile.email,
                    password=data['password']
                )
                user_profile.user = user
                user_profile.save()
                return core_utils.create_response(
                    data="",
                    code=200,
                    message="User profile created successfully"
                )
            else:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Passwords do not match"
                )
        else:
            return core_utils.create_response(
                data="",
                code=400,
                message="Form errors",
                extra=form.errors
            )


class SendFriendRequest(APIView):
    @method_decorator(login_required)
    @method_decorator(ratelimit(key='user', rate='3/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        try:
            request_body = request.data

            sender_profile = core_models.UserProfile.objects.get(email=request.user.email)
            receiver_email = request_body.get("action_to")

            if sender_profile.email == receiver_email:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="You cannot send a friend request to yourself"
                )

            try:
                receiver_profile = core_models.UserProfile.objects.get(email=receiver_email)
                if core_models.FriendRequest.objects.filter(sender=sender_profile, receiver=receiver_profile).exists():
                    return core_utils.create_response(
                        data="",
                        code=400,
                        message="Friend request already sent"
                    )

                form = core_forms.FriendRequestForm({"sender": sender_profile, "receiver": receiver_profile})
                if form.is_valid():
                    friend_request = form.save(commit=False)
                    friend_request.status = "pending"
                    friend_request.save()
                    return core_utils.create_response(
                        data="",
                        code=200,
                        message="Friend request sent successfully"
                    )
                else:
                    return core_utils.create_response(
                        data="",
                        code=400,
                        message="Form errors",
                        extra=form.errors
                    )
            except core_models.UserProfile.DoesNotExist:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Invalid receiver details for the friend request."
                )
        except Exception as e:
            return core_utils.create_response(
                data="",
                code=400,
                message=str(e)
            )


class FriendRequestAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            request_body = request.data
            action_to = request_body.get("action_to")
            action = request_body.get("action")
            
            if action not in ["accepted", "rejected"]:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Invalid action on friend request."
                )
            
            if not action_to:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="The 'action_to' parameter is required."
                )
            
            receiver_profile = core_models.UserProfile.objects.get(email=request.user.email)
            
            try:
                sender_profile = core_models.UserProfile.objects.get(email=action_to)
                friend_request = core_models.FriendRequest.objects.get(sender=sender_profile, receiver=receiver_profile)
                
                if not core_models.FriendRequest.objects.filter(sender=sender_profile, receiver=receiver_profile).exists():
                    return core_utils.create_response(
                        data="",
                        code=400,
                        message="No friend request between these users found"
                    )
                
                serializer = core_serializers.FriendRequestSerializer(friend_request, data={"status": action}, partial=True)
                
            except core_models.UserProfile.DoesNotExist:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Invalid sender details for the friend request."
                )
            
            if serializer.is_valid():
                if action == "accepted":
                    friend_request.accept()
                elif action == "rejected":
                    friend_request.reject()
                return core_utils.create_response(
                    data="",
                    code=200,
                    message="Friend request accepted/rejected successfully"
                )
            else:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Serializer errors",
                    extra=serializer.errors
                )
        
        except Exception as e:
            return core_utils.create_response(
                data="",
                code=400,
                message=str(e)
            )

    def get(self, request, *args, **kwargs):
        receiver_profile = core_models.UserProfile.objects.get(email=request.user.email)
        friend_requests = core_models.FriendRequest.objects.filter(receiver=receiver_profile, status="pending")
        serialized_requests = [{'from': request.sender.name, 'status': request.status} for request in friend_requests]
        
        return core_utils.create_response(
            data=serialized_requests,
            code=200
        )


class FriendsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        userProfile = core_models.UserProfile.objects.get(email=request.user.email)
        friends = userProfile.friends.all()
        serialized_friends = [friend.email for friend in friends]
        return core_utils.create_response(
            data=serialized_friends,
            code=200
        )


class SearchUsersAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            search_by = request.GET.get('search_by', 'name')
            page_number = int(request.GET.get('page', 1))
            query = request.GET.get('query', '')
            if search_by == "name":
                matching_users = core_models.UserProfile.objects.filter(name__icontains=query).order_by('name')
                paginator = Paginator(matching_users, 10)
                try:
                    page = paginator.page(page_number)
                except Exception as e:
                    return core_utils.create_response(
                        data="",
                        code=400,
                        message='Invalid page number'
                    )
                serialized_users = [{'id': user.id, 'name': user.name} for user in page]
                return core_utils.create_response(
                    data=serialized_users,
                    code=200,
                    extra={"total_pages": paginator.num_pages, "page": page_number}
                )
            elif search_by == "email":
                try:
                    matching_user = core_models.UserProfile.objects.get(email=query.lower())
                except core_models.UserProfile.DoesNotExist:
                    return core_utils.create_response(
                        data="",
                        code=400,
                        message='This user does not exist'
                    )
                serialized_user = {'id': matching_user.id, 'name': matching_user.name}
                return core_utils.create_response(
                    data=serialized_user,
                    code=200
                )
            else:
                return core_utils.create_response(
                    data="",
                    code=400,
                    message="Invalid value in 'search_by' param"
                )
        except Exception as e:
            return core_utils.create_response(
                data="",
                code=400,
                message=str(e)
            )


class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username').lower()
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return core_utils.create_response(
                data="",
                code=200,
                message="Login successful"
            )
        else:
            return core_utils.create_response(
                data="",
                code=401,
                message="Invalid credentials"
            )


from django.middleware.csrf import get_token

class CSRFTokenAPIView(APIView):
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return core_utils.create_response(
            data={"csrf_token": csrf_token},
            code=200
        )
