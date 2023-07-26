from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import (RegisterUserAPIView, LogoutView, UserProfile, UserFollower, ProfilesListView, BlockedProfile, ProfileBlockedList, UserProfileEdit, ChangePasswordView, UserInformationEdit,
                    UserProfileView, UserProfileFollowers, WorkAndEducationExperiance, UpdateWorkAndEducationExperiance, LanguageView, LanguageUpdateView,
                    ProfileResum, DeletProfile)


urlpatterns = [
    
    # signup:
    path('register/', RegisterUserAPIView.as_view(), name='user_registration'),
    # login:
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # logout
    path('logout/', LogoutView.as_view(), name='logout'),
    # refresh the token:
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # user profile:
    path('profile/', UserProfile.as_view(), name='userprofile'),
    # profile edite:
    path("profile/edit/",UserProfileEdit.as_view(), name='userprofiledit'),
    # change user password:
    path('profile/change/password/', ChangePasswordView.as_view(), name='changepassword'),
    # delete user accounts:
    path('profile/delete/',DeletProfile.as_view(), name='deletaccounts'),
    # user info update:
    path('user/update/',UserInformationEdit.as_view(),name='userupdateinfo'),
    # (user follower with delet) and (following list with add):
    path('profile/follower/', UserFollower.as_view(), name='userfollower'),
    # profile for adding and searching:
    path('profile/list/', ProfilesListView.as_view(), name='profilelistview'),
    # block a profile:
    path('profile/block/<int:pk>/', BlockedProfile.as_view(), name='blockedprofileview'),
    # the blocked list:
    path('profile/blocked/list/', ProfileBlockedList.as_view(), name='blockedlist'),
    # the other profile:
    path('profile/<int:pk>/', UserProfileView.as_view(), name='userprofileview'),
    # the others followers and followed by:
    path("profile/<int:pk>/follower/", UserProfileFollowers.as_view(),name= "userprofilefollowers"),
    # word and education experiance list and adding:
    path("profile/experiance/", WorkAndEducationExperiance.as_view(), name='workeducationexper'),
    # work and education experiance update and delet:
    path("profile/experiance/<int:pk>/", UpdateWorkAndEducationExperiance.as_view(), name='updateworkeducationexper'),
    # add language experianse:
    path("profile/language/", LanguageView.as_view(), name='addlanguage'),
    # update language and delete:
    path("profile/language/<int:pk>/", LanguageUpdateView.as_view(), name="languageupdate"),
    # the profile resum:
    path("profile/<int:pk>/resum/", ProfileResum.as_view(), name="profileresum")

]