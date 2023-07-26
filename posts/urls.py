from django.urls import path
from .views import NewPostView, NewsFeedView, EditPostView, ViewPostView, ProfileActivityView, EditComent


urlpatterns = [
    
    # new post:
    path("new/post/", NewPostView.as_view(), name='newpost' ),
    # edit post:
    path('<int:pk>/edit/', EditPostView.as_view(), name="editpost"),
    # edit a coment:
    path("comment/<int:pk>/edit/", EditComent.as_view(), name= "editcoment"),
    # veiw post:
    path('<int:pk>/post/', ViewPostView.as_view(), name= "postview"),
    # news feed:
    path('newsfeed/', NewsFeedView.as_view(), name='newsfeed'),
    # user activity:
    path('activity/', ProfileActivityView.as_view(), name="profileactivity")
]
