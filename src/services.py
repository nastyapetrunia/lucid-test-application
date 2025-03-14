from src.database.utils.schemas import UserCreate, Token
from src.database.utils.setup import get_db
from src.database.utils.models import User

def register_user():
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(username=user.username, password=hash_password(user.password))
    db.add(new_user)
    db.commit()