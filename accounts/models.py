from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries import countries
from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager
import os
import pycountry



def get_upload_path(instance, filename):
    # Get the username of the user
    username = instance.user.username
    # Create a folder with the username if it doesn't exist
    folder_path = os.path.join('media', username)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Return the path where the file will be stored
    return os.path.join(folder_path, filename)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class TaggedProfileManager(TaggableManager):
    content_object = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='tagged_items')

class Profile(models.Model):
    GENDER= [('f','female'),('m','male')]
    COUNTRY_LIST=[ name for name in countries]
    active= models.BooleanField(default=True)
    private= models.BooleanField(default= False)
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    photo= models.ImageField(upload_to=get_upload_path, height_field=None, width_field=None,
                              max_length=None, blank=True, null=True)
    bio= models.TextField(max_length=300, blank= True, null= True)
    follower= models.ManyToManyField('self', related_name= 'followed_by', blank= True, symmetrical= False)
    blocked_Profile= models.ManyToManyField('self', related_name='bloced_by', blank= True, symmetrical= False)
    country= models.CharField(choices= COUNTRY_LIST, null=True, blank= True, max_length= 15)
    city= models.CharField(max_length=50, null=True, blank=True)
    gender= models.CharField(choices= GENDER, max_length=6,null=True, blank=True)
    update= models.DateField(auto_now=True)
    phone= PhoneNumberField(blank= True, null= True)
    birthday= models.DateField(auto_now_add=False, null=True, blank=True)
    tags = TaggedProfileManager(blank=True)
    
    def tag_list(self):
        return [tag.name for tag in self.tags.all()]
    def __str__(self):
        return self.user.username

    def follower_count(self):
        return self.follower.count()
    
    def followed_by_count(self):
        return self.followed_by.count()

class WorkExpAndEducation(models.Model):
    INSTITUTETYPELIST= [('school','School'),('collage','Collage'),
                     ('institute','Institute'),('company','Company')]
    COUNTRY_LIST=[ name for name in countries]
    user= models.ForeignKey(Profile , on_delete=models.CASCADE, related_name='userexperiance')
    InstituteType= models.CharField(max_length=9, choices=INSTITUTETYPELIST, default='School', null=False, blank=False)
    InstituteType_name= models.CharField(max_length=50, null=True)
    InstituteType_phone= PhoneNumberField(blank= True, null= True)
    InstituteType_mail= models.EmailField(blank= True, null= True, max_length=254)
    start_date= models.DateField(blank= True, null= True)
    end_date= models.DateField( blank= True, null= True)
    posission= models.CharField( max_length=50, null=True, blank=True)
    department= models.CharField(max_length=50, null=True, blank=True)
    country= models.CharField(choices= COUNTRY_LIST, null=True, blank= True, max_length= 15)
    city= models.TextField(max_length= 30, null=True, blank=True)
    additional_info= models.CharField( max_length=60, blank=True, null=True)

    def __str__(self):
        return f'{self.user.user.username} went to {self.InstituteType_name}'



class Languge(models.Model):
    
    LEVELS=[("1",'A1'),("2",'A2'),("3",'B1'),("4",'B2'),
            ("5",'C1'),("6",'C2')]
    LANGUAGE_CHOICES = [(lang.name, lang.name) for lang in pycountry.languages]

    user= models.ForeignKey(Profile , on_delete=models.CASCADE)
    language = models.CharField(choices=LANGUAGE_CHOICES, blank=True, null=True, max_length=100)
    is_mother_tongue= models.BooleanField()
    reading_level= models.CharField(choices= LEVELS, max_length=2)
    writing_level= models.CharField(choices= LEVELS, max_length=2)
    listing_level= models.CharField(choices= LEVELS, max_length=2)

    def __str__(self):
        return f'{self.user.user.username} has a ^{self.language}^ language'
    