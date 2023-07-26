from .models import Post, Comment

#  function for up/down and comment on a post:
def handle_action(user, post_id, action, coment=None):
    # add the up/down request and check if the user has down/up the post in the past, than remove the old active:
        # add up active to the post:
    try:
        # add up active to the post:
        post = Post.objects.get(id=post_id)
        if action == 'up':
            if user in post.down.all():
                post.down.remove(user)
                post.up.add(user)
            elif user in post.up.all():
                post.up.remove(user)
            else:
                post.up.add(user)
            return {"success": "Your upvote has been added!"}

        # add down active to the post:
        elif action == 'down':
            if user in post.up.all():
                post.up.remove(user)
                post.down.add(user)
            elif user in post.down.all():
                post.down.remove(user)
            else:
                post.down.add(user)
            return {"success": "Your downvote has been added!"}

        # add comment to the post:
        elif action == 'coment':
            if post.post_coments.filter(user=user).count() >= 3:
                return {"error": "You have commented 3 times!"}
            else:
                Comment.objects.create(user=user, post=post, text=coment)
                return {"success": "Your comment has been added!"}

    except Post.DoesNotExist:
        return {"error": "Post not found"}