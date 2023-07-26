from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, WorkExpAndEducation, Languge
from posts.models import Post, Comment
from django.shortcuts import get_object_or_404 
from django.http import Http404
from rest_framework.exceptions import APIException
from rest_framework import filters
from .serializers import (RegisterSerializer,UserProfileSerilizer, UserFollowerSerializer, FollowerSerializer, UserUpdateSerializer,UserProfilEditSerilizer, UserUpdatePasswordSerializer,
                         WorkEducExpSerializer, LanguageSerializer, ResumSerilizer)

from django.db.models import Q
from functools import reduce # Python 3, use "reduce"
import operator
from posts.helpers import handle_action



# signup
class RegisterUserAPIView(APIView):
  permission_classes = (AllowAny,)
  serializer_class = RegisterSerializer
  def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# logout:
class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Retrieve the refresh token from the request
            refresh_token = request.auth

            # Delete the refresh token from the database
            RefreshToken(refresh_token).blacklist()

            return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# user profile:
class UserProfile(generics.ListCreateAPIView):
    serializer_class= UserProfileSerilizer
    authentication_classes = [JWTAuthentication]
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        # return self.request.user.profile
        profile= Profile.objects.get(user= self.request.user)
        return profile
    
    def list(self, request, *args, **kwargs):
        instance= self.get_queryset()
        posts_list= []
        try:
            posts= Post.objects.filter(user= instance)
            if posts:
                for post in posts:
                    coment= Comment.objects.filter(post= post)
                    post_data= {
                        'id':post.id,
                        'user': post.user.user.username,
                        'text': post.text,
                        'image': post.image.url if post.image else None,
                        'date_published': post.date_publish,
                        'date_update': post.date_update if post.date_update!=post.date_publish else None,
                        'up_counts': post.up_count(),
                        'down_counts': post.down_count(),
                        'comment counts':coment.count(),
                       }
                    posts_list.append(post_data)
            else:
                raise APIException()

        except APIException:
            post_data= {"error":"you don't have any posts yet! post something now!"}
            posts_list.append(post_data)

        user_data = {
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'username':instance.user.username,
            'id':instance.user.id,
            'active':instance.active,
            'photo': instance.photo.url if instance.photo else None,
            'bio': instance.bio,
            'country': instance.country,
            'city': instance.city,
            'tags': [tag.name for tag in instance.tags.all()],
            'followers_count': instance.follower.count(),
            'followed_by_count': instance.followed_by.count(),
            'blocked_Profiles_counts':instance.blocked_Profile.count()
            }
        
        try:

        #   get the user profile and tags, than getting the users how have the same interesting:
            profile= self.request.user.profile
            profile_tags= [tag.name for tag in profile.tags.all()]
            tag_filters = [Q(tags__name=tag) for tag in profile_tags]
            profiles = Profile.objects.filter(reduce(operator.or_, tag_filters)).exclude(user= profile.user)
            

        #   get the users who have the same tags in a list:
            users_list=[]
            suggesting_tags= {}
            for user in profiles.all():
                if user not in users_list:
                    users_list.append(user)

        #   get the users tags in a list:
            tags_list=[]
            for user in users_list:
                user_tags=[tag.name for tag in user.tags.all()]
                tags_list.append(user_tags)

        #   extracte the complexe list into a single list and exclude the tags that the user have:
            extract_list= []
            for tag in tags_list:
                for item in tag:
                    if item not in profile_tags:
                        extract_list.append(item)

        #   put the tags into dictionary with value if the times that tags appear in the other profiles:
            for i in extract_list:
                if i not in suggesting_tags:
                    suggesting_tags[i]= 1
                else:
                    value= suggesting_tags[i]
                    value+= 1
                    suggesting_tags[i]= value

        #   sort the dictionary by the max tags that appear in the profiles:
            sorted_dic= sorted(suggesting_tags.items(), key= lambda x:x[1], reverse=True)
            tags= [tag for tag in sorted_dic[:3]]
            
        #   check if user have english skills and check his level on it:
            try:
                profile_english= Languge.objects.get(user= profile, language= "English")
                sum= int(profile_english.reading_level)+ int(profile_english.writing_level)+ int(profile_english.listing_level)
                if sum < 12:
                    language_suggesting=(f"u must grow up your english skills, must of the employee have more english experiance, so growing your language open more doors for u!")
            except:
                language_suggesting=(f"most of the emplyee have english skills, u must start with!")

        except:
            profiles= "why don't u start learning something new today!"


        data = {'user_data': user_data, 'post_data':posts_list, "suggestion tags:": tags, "language_suggesting": language_suggesting}
        return Response(data)
    

    def post(self, request, *args, **kwargs):
        user= self.request.user.profile
        post_id= request.data.get("post_id")
        action= request.data.get("action")
        if action=="coment":
            coment= request.data.get("coment")
            result= result =handle_action(user, post_id, action, coment)
        else:
            result= result = handle_action(user, post_id, action)
        return Response(result)
        

# user profile edite:
class UserProfileEdit(generics.RetrieveUpdateAPIView):
    serializer_class= UserProfilEditSerilizer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_object(self):
        return self.request.user.profile
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



# change password:
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class= UserUpdatePasswordSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    def get_object(self):
        user= self.request.user
        return user
    def update(self, request, *args, **kwargs):
        self.object= self.get_object()
        serializer= self.get_serializer(data= request.data)
        if serializer.is_valid():
            if self.object.check_password(serializer.data.get('oldpass')):
                self.object.set_password(serializer.data.get('newpass'))
                self.object.save()
                return Response({"success":"your password has been changed!"}, status= status.HTTP_202_ACCEPTED)
            else:    
                return Response({"error":"your password is wrong!"}, status= status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)


# edit user info
class UserInformationEdit(generics.RetrieveUpdateAPIView):
    serializer_class= UserUpdateSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    def get_object(self):
        return self.request.user
    

# delet the user profile:
class DeletProfile(generics.DestroyAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    
    def get_object(self):
        user= self.request.user
        return user.profile


# user (following with add) and (follower with delet):
class UserFollower(generics.RetrieveDestroyAPIView):
    serializer_class = UserFollowerSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        profile_id = self.request.user.id
        queryset = Profile.objects.prefetch_related('follower').filter(id=profile_id)
        return get_object_or_404(queryset)


    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile_id = request.data.get('profile_id')
        action= request.data.get("action")
        follower_profile = get_object_or_404(Profile, id=profile_id)
        if action== "unfollow":
            if follower_profile in profile.follower.all():
                profile.follower.remove(follower_profile)
                return Response({'success': 'the follower has been removed'},status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': 'Profile not found in follower list.'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        profile_id= request.data.get("profile_id")
        action= request.data.get("action")
        following_profile= get_object_or_404(Profile, id=profile_id)
        if action== "follow":
            try:
                profile.follower.add(following_profile)
                return Response({'success': 'the profile has been add to your following list'},status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# Profiles list with add:
class ProfilesListView(generics.ListAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    serializer_class= FollowerSerializer
    filter_backends= [filters.SearchFilter,]
    search_fields= ['user__username','tags__name']

    def get_queryset(self):
        user= self.request.user.profile

        blocked_profile= Profile.objects.filter(blocked_Profile= user)
        profile= Profile.objects.filter(user= user.user)
        follower_profile= user.follower.all()
        exclude_profile= list(blocked_profile | follower_profile | profile)
        
        profiles= Profile.objects.exclude(pk__in=[p.pk for p in exclude_profile])
        search_query = self.request.query_params.get('search', None)
        if search_query:
            exclude_profile= list(blocked_profile | profile)
            profiles= Profile.objects.exclude(pk__in=[p.pk for p in exclude_profile])
        return profiles
    
    def post(self, request, *args, **kwargs):
        profile = self.request.user.profile
        profile_id= request.data.get("profile_id")
        action= request.data.get("action")
        following_profile= get_object_or_404(Profile, id=profile_id)
        if action == "follow":
            try:
                profile.follower.add(following_profile)
                return Response({'success': 'the profile has been add to your following list'},status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# the blocked profiles:
class BlockedProfile(generics.RetrieveAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    serializer_class=  FollowerSerializer
    
    def get_object(self):
        profile= self.request.user.profile
        return profile

    def post(self, request, *args, **kwargs):
        profile= self.request.user.profile
        blockedprofile= get_object_or_404(Profile, id= self.kwargs['pk'])
        profile.blocked_Profile.add(blockedprofile)

        if blockedprofile in profile.follower.all():
            profile.follower.remove(blockedprofile)
        
        if profile in blockedprofile.follower.all():
            blockedprofile.follower.remove(profile)
        
        return Response({"success":"u successfuly blocked this user!"}, status= status.HTTP_202_ACCEPTED)


# blocked list:
class ProfileBlockedList(generics.ListCreateAPIView):
    serializer_class= FollowerSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_queryset(self):
        profile= self.request.user.profile
        return profile.blocked_Profile.all()
    
    def post(self, request, *args, **kwargs):
        profile= self.request.user.profile
        profile_id= self.request.data.get('profile_id')
        action= request.data.get("action")
        if action== 'unblock':
            try:
                profile.blocked_Profile.remove(profile_id)
                return Response({"success":"you successfully unblocked the user"}, status=status.HTTP_202_ACCEPTED)
            except:
                return Response({"error":"the user not found or bad request!"}, status=status.HTTP_400_BAD_REQUEST)


# the others profile view:
class UserProfileView(generics.ListAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_queryset(self):
        profile= self.request.user.profile
        user_profile= Profile.objects.get(id= self.kwargs['pk'])
        if profile not in user_profile.blocked_Profile.all() and user_profile not in profile.blocked_Profile.all():
            return user_profile
        else:
            raise PermissionDenied(detail="Access Denied!")


    def list(self, request, *args, **kwargs):
        instance= self.get_queryset()
        profile_data= {
            "user name":instance.user.username,
            "active": instance.active,
            "private": instance.private,
            "photo": instance.photo.url if instance.photo else None,
            "bio": instance.bio,
            "country": instance.country,
            "city": instance.city,
            "follower_count": instance.follower_count(),
            "followed_by_count": instance.followed_by_count(),
            "tags": [tag.name for tag in instance.tags.all()]
        }
        post_list= []
        try:
            posts= Post.objects.filter(user= instance)
            if posts:
                for post in posts.all():
                    post_data={
                        "id":post.id,
                        "text": post.text,
                        "image": post.image.url if post.image else None,
                        "date_publish": post.date_publish,
                        'date_update': post.date_update if post.date_update != post.date_publish else None,
                        "up_count": post.up_count(),
                        "down_count": post.down_count(),
                        "user name": post.user.user.username,
                        "photo": post.user.photo.url if post.user.photo else None
                    }
                    post_list.append(post_data)
            else:
                post_data= {"error":"the user dosn't have a posts yet!"}
                post_list.append(post_data)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        data= {"user information":profile_data, "posts":post_list}
        return Response(data)

    def post(self, request, *args, **kwargs):
        profile= self.request.user.profile
        user_profile= self.get_queryset()
        action= request.data.get("action")

        try:
            # follow the profile:
            if action== 'follow':
                if user_profile not in profile.follower.all():
                    profile.follower.add(user_profile)
                else:
                    return Response({"error":"u already follow this account!"}, status= status.HTTP_406_NOT_ACCEPTABLE)
                    
            
            # unfollow the profile:
            if action== "unfollow":
                if user_profile in profile.follower.all():
                    profile.follower.remove(user_profile)
                else:
                    return Response({"error":"u don't follow this acount already!"}, status= status.HTTP_406_NOT_ACCEPTABLE)
                

             # up the psot:
            if action== "up":
                post_id= request.data.get("post_id")
                post= Post.objects.get(id= post_id)
                if profile in post.down.all():
                    post.down.remove(profile)
                    post.up.add(profile)
                elif profile in post.up.all():
                    post.up.remove(profile)
                    return  Response({"success":"your up has been removed"}, status= status.HTTP_201_CREATED)
                else:
                    post.up.add(profile)
                return  Response({"success":"your up has been added!"}, status= status.HTTP_201_CREATED)
            
            # down the post:
            if action== "down":
                post_id= request.data.get("post_id")
                post= Post.objects.get(id= post_id)
                if profile in post.up.all():
                    post.up.remove(profile)
                    post.down.add(profile)
                elif profile in post.down.all():
                    post.down.remove(profile)
                    return  Response({"success":"your down has been removed"}, status= status.HTTP_201_CREATED)
                else:
                    post.down.add(profile)
                return  Response({"success":"your down has been added!"}, status= status.HTTP_201_CREATED)
        

            # add coment to the post:
            if action=='coment':
                post_id= request.data.get("post_id")
                post= Post.objects.get(id= post_id)
                text= request.data.get('coment')
                if post.post_coments.filter(user= profile).count() >= 3:
                    return Response({"error":"u have coment 3 times!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    Comment.objects.create(user=profile, post=post, text=text)
                    return Response({"success":"your comment has been added!"}, status= status.HTTP_201_CREATED)
            

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
class UserProfileFollowers(generics.RetrieveAPIView):
    permission_classes= [IsAuthenticated,]
    # authentication_classes= [JWTAuthentication,]
    serializer_class= UserFollowerSerializer

    def get_object(self, *args, **kwargs):
        profile_id= self.kwargs['pk']
        profile = Profile.objects.prefetch_related('follower').filter(id=profile_id)
        return get_object_or_404(profile)
    
    def post(self, request, *args, **kwargs):
        try:
            user_id= request.data.get("profile_id")
            action= request.data.get("action")
            profile= self.request.user.profile
            if action== "follow":
                if user_id not in profile.follower.all():
                    profile.follower.add(user_id)
                    return Response({"success":"u follow this account now!"}, status= status.HTTP_201_CREATED)
                else:
                    return Response({"error":"u already follow this account!"}, status= status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            # return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error":"u already follow this account!"}, status= status.HTTP_406_NOT_ACCEPTABLE)
            






# list and create a work experiance:
class WorkAndEducationExperiance(generics.ListCreateAPIView):
    serializer_class= WorkEducExpSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_queryset(self):
        user= self.request.user
        return Profile.objects.get(user= user)
    
    def perform_create(self, serializer):
        profile = self.request.user.profile
        serializer.validated_data['user'] = profile
        serializer.save()

    def list(self, request, *args, **kwargs):
        profile= self.get_queryset()
        work_edu_list=[]
        try:
            work_edu= WorkExpAndEducation.objects.filter(user= profile)
            if work_edu:
                for instance in work_edu:
                    work_edu_data= {
                    'InstituteType': instance.InstituteType,
                    'InstituteType_name': instance.InstituteType_name,
                    "phone":str(instance.InstituteType_phone) if instance.InstituteType_phone else None,
                    'InstituteType_email': instance.InstituteType_mail,
                    'start_date': instance.start_date,
                    'end_dat': instance.end_date,
                    'posission': instance.posission,
                    'department': instance.department,
                    'country': instance.country,
                    'city': instance.city,
                    'additional_info': instance.additional_info }
                    work_edu_list.append(work_edu_data)
            else:
                raise APIException()
            
        except APIException:
            work_edu_data= {"error":"user doesn't have any work experiance or Education experiance"}
            work_edu_list.append(work_edu_data)

        institutetype= WorkExpAndEducation.INSTITUTETYPELIST
        country= WorkExpAndEducation.COUNTRY_LIST
        data = {'work and education experiance ': work_edu_list,'institute type':institutetype, 'country':country}
        return Response(data)


# update and delete work and experiance object:
class UpdateWorkAndEducationExperiance(generics.RetrieveUpdateDestroyAPIView):
    serializer_class= WorkEducExpSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_object(self):
        profile = self.request.user.profile
        pk = self.kwargs['pk']
        work_edu = get_object_or_404(WorkExpAndEducation, id=pk)
        if work_edu.user == profile:
            return work_edu
        else:
            raise Http404("Access Denied!")

    def perform_update(self, serializer):
        profile = self.request.user.profile
        instance = serializer.save(user=profile)
        instance.save()

    def perform_destroy(self, instance):
        instance.delete()


# list and create a language:
class LanguageView(generics.ListCreateAPIView):
    serializer_class= LanguageSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_queryset(self):
        profile= self.request.user.profile
        return Languge.objects.filter(user= profile)
    
    def perform_create(self, serializer):
        # Set the user field to the current user's profile
        profile = self.request.user.profile
        serializer.validated_data['user'] = profile
        serializer.save()

    def list(self, request, *args, **kwargs):
        language_choices = Languge.LANGUAGE_CHOICES
        levels= Languge.LEVELS
        language_choices = sorted(language_choices, key=lambda x: x[0].lower())
        language_names = [lang[1] for lang in language_choices]
      
        try:
            lang_list= []
            user= self.request.user.profile
            language= Languge.objects.filter(user= user)
      
            if language:
                for instance in language.all():
                    language_data= {
                        'language': instance.language,
                        'is_mother_tongue': instance.is_mother_tongue,
                        'reading_level': instance.reading_level,
                        'writing_level': instance.writing_level,
                        'listing_level': instance.writing_level
                        }
                    lang_list.append(language_data)
            else:
                raise APIException()
      
        except APIException:
            language_data= {"error":"user dosn't have any language experianse!"}
            lang_list.append(language_data)

        data = {'languages': language_names, "levels":levels, 'language':lang_list}
        return Response(data)
    

# update a language or delete it:
class LanguageUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class= LanguageSerializer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_object(self):
        profile =self.request.user.profile
        language_id= self.kwargs['pk']
        language= Languge.objects.get(user= profile, id= language_id)
        if language.user == profile:
            return language
        else:
            raise Http404("Access Denied!")

    def perform_update(self, serializer):
        profile = self.request.user.profile
        instance = serializer.save(user=profile)
        instance.save()

    def perform_destroy(self, instance):
        instance.delete()


# view the user resum:
class ProfileResum(generics.ListAPIView):
    serializer_class= ResumSerilizer
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_queryset(self):
        profile= Profile.objects.get(id= self.kwargs['pk'])
        user= self.request.user
        # allow to view the resum for the unblocked user and for the owner of the profile and for the user how follow the profile or the user how the profile folllow him:
        if user.profile not in profile.blocked_Profile.all() and profile.user== user or profile in user.profile.follower.all() or user.profile in profile.follower.all():
            return profile
        else:
            raise PermissionDenied(detail="You are not allowed to view this resum!")

    def list(self, request, *args, **kwargs):
        profile= self.get_queryset()
        language_list=[]
        try:
            languages= Languge.objects.filter(user= profile)
            if languages:
                for instance in languages:
                    language= {
                    'language': instance.language,
                    'is_mother_tongue': instance.is_mother_tongue,
                    'reading_level': instance.reading_level,
                    'writing_level': instance.writing_level,
                    'listing_level': instance.writing_level}
                    language_list.append(language)
            else:
                raise APIException()
        except APIException:
            language= {"error":"user dosn't have any language experianse!"}
            language_list.append(language)
        work_edu_list=[]
        try:
            work_edu= WorkExpAndEducation.objects.filter(user= profile)
            if work_edu:
                for instance in work_edu:
                    work_edu_data= {
                    'InstituteType': instance.InstituteType,
                    'InstituteType_name': instance.InstituteType_name,
                    'InstituteType_phone': str(instance.InstituteType_phone) if instance.InstituteType_phone else None,
                    'InstituteType_email': instance.InstituteType_mail,
                    'start_date': instance.start_date,
                    'end_dat': instance.end_date,
                    'posission': instance.posission,
                    'department': instance.department,
                    'country': instance.country,
                    'city': instance.city,
                    'additional_info': instance.additional_info
                        }
                    work_edu_list.append(work_edu_data)
            else:
                raise APIException()
            
        except APIException:
            work_edu_data= {'error': "user doesn't have any work experiance or Education experiance"}
            work_edu_list.append(work_edu_data)

        user_data = {
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'email': profile.user.email,
            'photo': profile.photo.url if profile.photo else None,
            'bio': profile.bio,
            'country': profile.country,
            'city': profile.city,
            'gender': profile.gender,
            'phone': str(profile.phone) if profile.phone else None,
            'birthday': profile.birthday,
            'tags': [tag.name for tag in profile.tags.all()]
            } 
        
        data = {'user_data': user_data, 'languages': language_list, 'work and education':work_edu_list}
        return Response(data)
    