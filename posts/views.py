from rest_framework import generics, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Post, Comment
from .serializers import NewPostSerializer, EditPostSerializer, CommentSerializer, PostDetails, EditCommentSerializer
from rest_framework.response import Response
from .helpers import handle_action
from rest_framework.exceptions import APIException



# new post:
class NewPostView(generics.CreateAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    serializer_class= NewPostSerializer

    def post(self, request, *args, **kwargs):
        profile= self.request.user.profile
        serializer= NewPostSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save(user= profile)
            return Response({"success":"your post has been publish!"}, status= status.HTTP_201_CREATED)
        else:
            return Response({"error":"an error acource during the uploading process!"}, status= status.HTTP_400_BAD_REQUEST)
        


# edit psot:
class EditPostView(generics.RetrieveUpdateAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    serializer_class= EditPostSerializer
    def get_object(self):
        post= Post.objects.get(id= self.kwargs['pk'])
        if post.user== self.request.user.profile:
            return post
        
    def perform_update(self, serializer):
        post= self.get_object()
        if post.user== self.request.user.profile:
            instance= serializer.save(post= post)
            instance.save()
        else:
            return Response


# edit comment:
class EditComent(generics.RetrieveUpdateAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]
    serializer_class= EditCommentSerializer

    def get_object(self):
        coment= Comment.objects.get(id= self.kwargs["pk"])
        return coment
    
    def update(self, request, *args, **kwargs):
        comment= self.get_object()
        if comment.user== self.request.user.profile:
            serializer= self.get_serializer(comment, data= request.data, partial= True)
            if serializer.is_valid():
                serializer.save()
                return Response({"sucsuss":"your comment has been edit!"}, status= status.HTTP_200_OK)
            else:
                return Response({"bad":"an error acourc"}, status= status.HTTP_200_OK)
        else:
            return Response({"error":"it's not your comment to edit!"}, status= status.HTTP_200_OK)
        
            

# view post details:
class ViewPostView(generics.ListCreateAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_object(self):
        post= Post.objects.get(id= self.kwargs["pk"])
        return post
    
    def list(self, request, *args, **kwargs):
        post= self.get_object()
        comment_serializer = CommentSerializer(post.post_coments.all(), many=True)
        post_serializer= PostDetails(post)
        response_data = {
            "post_data": post_serializer.data,
            "comments": comment_serializer.data
        }
        return Response(response_data)
    
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




# news feed:
class NewsFeedView(generics.ListAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]

    def get_queryset(self):
        profile= self.request.user.profile
        return profile

    def list(self, request, *args, **kwargs):
        post_list= []
        profile= self.get_queryset()
        followers= profile.follower.all()
        for follower in followers:
            posts= Post.objects.filter(user=follower).exclude(seen_by= profile)
            if posts:
                for post in posts:
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
        data= {"post_data":post_list}
        return Response (data)
    

    def post(self, request):
        try:
            profile= self.get_queryset()
            action= request.data.get("action")
            post= Post.objects.get(id= request.data.get("post_id"))
            
            # seen the post:
            if action == "seen":
                post.seen_by.add(profile)
                return Response({"success":"u have now seen the post"}, status= status.HTTP_202_ACCEPTED)

            # up the psot:
            if action== "up":
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
                text= request.data.get('coment')
                if post.post_coments.filter(user= profile).count() >= 3:
                    return Response({"error":"u have coment 3 times!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    Comment.objects.create(user=profile, post=post, text=text)
                    return Response({"success":"your comment has been added!"}, status= status.HTTP_201_CREATED)
        except:
            return Response({"error":"something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


# profile activity:
class ProfileActivityView(generics.ListAPIView):
    permission_classes= [IsAuthenticated,]
    authentication_classes= [JWTAuthentication,]


    def get_queryset(self):
        profile= self.request.user.profile
        return profile
    
    def list(self, request, *args, **kwargs):
        profile= self.get_queryset()
        liactivity= []
        
        try:
            postsup= Post.objects.filter(up= profile)
            for post in postsup:
                liactivity.append(f"you up {post.user.user.username} post")
        except:
            pass


        try:

            postdown= Post.objects.filter(down= profile)
            for post in postdown:
                liactivity.append(f"u down {post.user.user.username} post")
        except:
            pass
    

        try:
            comments= Comment.objects.filter(user= profile)
            for comment in comments:
                liactivity.append(f"you commented on {comment.post.user.user.username} post")
        except:
            pass

        sorted_liactivity= sorted(liactivity, reverse=True)
        data= {"activity: ": sorted_liactivity}
        return Response(data)