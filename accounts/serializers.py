from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, WorkExpAndEducation, Languge
from posts.models import Post
from django.contrib.auth.hashers import make_password
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

# signup
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields= ['username','email','password','first_name','last_name']
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(RegisterSerializer, self).create(validated_data)


# user info:
class UserSerializer(serializers.Serializer):
    username= serializers.ReadOnlyField()
    first_name= serializers.ReadOnlyField()
    last_name= serializers.ReadOnlyField()
    email= serializers.ReadOnlyField()
    class Meta:
        model= User
        fields= ['username' ,'first_name', 'last_name', 'email']


# user update info
class UserUpdateSerializer(serializers.ModelSerializer):
    username= serializers.ReadOnlyField()
    class Meta:
        model= User
        fields= ['username','first_name',"last_name", 'email']
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
        return super().update(instance, validated_data)

# blocked_user
# profile info for the friends list:
class ProfileListSerializer(serializers.Serializer):
    user= UserSerializer(read_only= True)
    class Meta:
        model= Profile
        field= ['user', 'photo','bio']



# user posts:
class ProfilePostsserializer(serializers.ModelSerializer):
    class Meta:
        model= Post
        fields= '__all__'


# user profile:################################################################################33
class UserProfileSerilizer(TaggitSerializer,serializers.ModelSerializer):
    # tags = TagListSerializerField()
    # followers_count= serializers.SerializerMethodField()
    # followed_by_count= serializers.SerializerMethodField()
    # user= UserSerializer(read_only= True)
    # # posts= ProfilePostsserializer()
    # class Meta:
    #     model= Profile 
    #     fields=['user', 'id', 'active', 'photo', 'bio','country', 'city', 'phone',
    #              'followers_count', 'followed_by_count', 'blocked_Profile','tags']

    # def get_followers_count(self, obj):
    #     return obj.follower.count()
    
    # def get_followed_by_count(self, obj):
    #     return obj.followed_by.count()
    
    # def get_blocked_Profile(self, obj):
    #     blockedlist= [bu.username for bu in obj.blocked_Profile.all()]
    #     return blockedlist
    pass

class UserProfilEditSerilizer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Profile
        fields = ['user', 'id', 'active', 'photo', 'bio', 'country', 'city', 'phone', 'birthday', 'gender', 'private', 'tags']


# user update password:
class UserUpdatePasswordSerializer(serializers.Serializer):
    model= User
    oldpass= serializers.CharField(required= True)
    newpass= serializers.CharField(required= True)


# list follower:
class FollowerSerializer(TaggitSerializer ,serializers.ModelSerializer):
    user= UserSerializer( read_only=True)
    following = serializers.SerializerMethodField()
    # tags = serializers.StringRelatedField(many=True)
    tags= TagListSerializerField()
    class Meta:
        model = Profile
        fields = ['user', 'photo', 'bio','id', 'following','tags']
    def get_following(self, obj):
        user = self.context["request"].user.profile
        return user.follower.filter(id=obj.id).exists()
class UserFollowerSerializer(serializers.Serializer):
    follower = FollowerSerializer(many=True, read_only=True)
    followed_by= FollowerSerializer(many=True, read_only=True)
    class Meta:
        model= Profile
        fields= ['follower', 'followed_by']


# others profile view:

    

# Work and education:
class WorkEducExpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id= serializers.ReadOnlyField()
    class Meta:
        model = WorkExpAndEducation
        fields = ['user', 'InstituteType', 'InstituteType_name', 'InstituteType_phone', 'InstituteType_mail', 'start_date',
                  'end_date', 'posission', 'department', 'city', 'additional_info','id']



# add language:
class LanguageSerializer(serializers.ModelSerializer):
    id= serializers.ReadOnlyField()
    class Meta:
        model= Languge
        fields= ['language', 'is_mother_tongue', 'reading_level',
                 'writing_level', 'listing_level', 'id'  ]
        
# resum serilizers:
class ResumSerilizer(TaggitSerializer,serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model= Profile
        fields= ['user', 'id', 'active', 'photo', 'bio','country', 'city', 'phone',
                 'birthday', 'gender','tags']
