from django.urls import path
from core import views as core_views
from core.views import CSRFTokenAPIView

urlpatterns = [
    path('create_user_profile/', core_views.CreateUserProfile.as_view(), name='create_user_profile'),
    path('send_friend_request/', core_views.SendFriendRequest.as_view(), name='send_friend_request'),
    path('friend_request/', core_views.FriendRequestAPIView.as_view(), name='friend_request'),
    path('friends/', core_views.FriendsAPIView.as_view(), name='friends'),
    path('search_users/', core_views.SearchUsersAPIView.as_view(), name='search_users'),
    path('user_login/', core_views.UserLoginAPIView.as_view(), name='user_login'),
    path('csrf_token/', CSRFTokenAPIView.as_view(), name='csrf_token'),

]
