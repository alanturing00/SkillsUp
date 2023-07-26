from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Profile, Comment


# new post:
class NewPostSerializer(serializers.ModelSerializer):
    class Meta:
        model= Post
        fields= ['text','image']


# edit post
class EditPostSerializer(serializers.ModelSerializer):
    class Meta:
        model= Post
        fields= ["id",'text','image']


class ViewPostSerializer(serializers.ModelSerializer):
    class Meta:
        model= Profile
        fields= ["id","photo", "birthday"]



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields= ["id","username","first_name","last_name",]


# edit comment:
class EditCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model= Comment
        fields= ["id","text","date_coment_pub","date_coment_upd"] 


# the post details:
class ProfileSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    class Meta:
        model= Profile
        fields= ["id","photo","user"]
class CommentSerializer(serializers.ModelSerializer):
    user= ProfileSerializer()
    class Meta:
        model= Comment
        fields= ["user","id","text","date_coment_pub","date_coment_upd"]
class PostDetails(serializers.ModelSerializer):
    user= ProfileSerializer()
    class Meta:
        model= Post
        fields= ["user","id","text","image","date_publish","date_update","up_count","down_count"]

