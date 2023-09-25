def user_serializer(user):
    return {
        "id": str(user["_id"]),
        "name": user['name'],
        "username": user['username'],
        "email": user['email'],
        "phoneNumber": user['phoneNumber'],
        "followers": user['followers'],
        "followings": user['followings'],
        "gender": user['gender']
    }

def status_serializer(status):
    return {
        "user_id": status['user_id'],
        "content": status['content'],
        "caption": status['caption'],
        "created_at": str(status['created_at']),
        "expired_at": str(status['expired_at']),
        "privacy": status['privacy'],
        "is_expired": status['is_expired']
    }

def post_serializer(post):
    return {
        "user": post['user'],
        "content": post['content'],
        "caption": post['caption'],
        "likes": post['likes'],
        "comments": post['comments'],
        "created_at": str(post['created_at']),
        "updated_at": str(post['updated_at']),
    }

def comment_serializer(comment):
    return {
        "user": comment['user'],
        "post_id": comment['post_id'],
        "text": comment['text'],
        "created_at": str(comment['created_at'])
    }