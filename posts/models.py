from django.db import models
from accounts.models import Profile
import os


def get_upload_to(instance, filename):
    username= instance.user.user.username
    folder_path = os.path.join('media', username)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return os.path.join(folder_path, filename)


class Post(models.Model):
    user= models.ForeignKey(Profile, related_name='posts', on_delete=models.CASCADE)
    text= models.CharField(null= True, blank= True, max_length=200)
    image= models.ImageField(null=True, blank= True, upload_to=get_upload_to, height_field=None, width_field=None, max_length=None)
    date_publish= models.DateTimeField (auto_now_add=True)
    date_update= models.DateTimeField(auto_now=True)
    up= models.ManyToManyField(Profile,related_name='upost', blank=True)
    down= models.ManyToManyField(Profile, related_name='downpost' , blank=True)
    seen_by= models.ManyToManyField(Profile, related_name= 'seend', blank=True)

    def __str__(self):
        return f'{self.user.user.username} has post new post at {self.date_publish}'
    
    class Meta():
        ordering= ('user',)
    
    def up_count(self):
        return self.up.count()

    def down_count(self):
        return self.down.count()
    
    
class Comment(models.Model):
    user= models.ForeignKey(Profile, related_name='comented_by', on_delete=models.CASCADE)
    post= models.ForeignKey(Post, related_name='post_coments', on_delete=models.CASCADE)
    text= models.CharField(max_length=100, null=False, blank=False)
    date_coment_pub= models.DateTimeField(auto_now_add=True)
    date_coment_upd= models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.user.username} has coment on {self.post.user.user.username} post'
    
    class Meta:
        ordering= ('date_coment_pub','date_coment_upd',)