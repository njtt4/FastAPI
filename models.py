from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base
import passlib.hash as _hash

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    # image_file = Column(String(20), nullable=False, default='default.jpg')
    hashed_password = Column(String(60), nullable=False)


    posts = relationship("Post", back_populates="owner", lazy=True)

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)

    # def __repr__(self) -> str:
    #     return f"User('{self.id}', '{self.email}', '{self.image_file}')"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    date_posted = Column(DateTime, nullable=False, default=datetime.utcnow )
    content = Column(String, index=True)

    owner = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"Post('{self.title}', '{self.date_posted}', '{self.content}')"