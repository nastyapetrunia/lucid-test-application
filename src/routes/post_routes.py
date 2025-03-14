from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from src.database.utils.setup import get_db
from src.services.auth import get_current_user
from src.database.utils.models import User, Post
from src.utils.cache import cache_posts, get_cached_posts
from src.database.utils.schemas import PostCreate, PostResponse

post_router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)

@post_router.post("/", response_model=PostResponse)
def add_post(post: PostCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Create a new post."""
    if len(post.text.encode('utf-8')) > 1048576:  # Max 1 MB
        raise HTTPException(status_code=400, detail="Payload too large.")

    db_user = db.query(User).filter(User.email == current_user).first()
    new_post = Post(text=post.text, user_id=db_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    cache_posts(db_user.id, None)

    return new_post


@post_router.get("/", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Get all posts for the current user."""
    db_user = db.query(User).filter(User.email == current_user).first()

    cached_posts = get_cached_posts(db_user.id)
    if cached_posts:
        return cached_posts

    posts = db.query(Post).filter(Post.user_id == db_user.id).all()
    cache_posts(db_user.id, [post.__dict__ for post in posts])

    return posts


@post_router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Delete a specific post."""
    db_user = db.query(User).filter(User.email == current_user).first()
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == db_user.id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    db.delete(post)
    db.commit()

    # Invalidate cache after deleting a post
    cache_posts(db_user.id, None)

    return {"detail": "Post deleted successfully"}
