from database import Base
from sqlalchemy import String, Integer, Column, DateTime, Identity

class Mahasiswa(Base):
    __tablename__ = 'mahasiswa'
    npm = Column(String(15), nullable=False, unique=True, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    client_secret = Column(String(40), nullable=False, unique=True)
    client_id = Column(Integer, Identity(start=1, cycle=True), nullable=False, unique=True)
    access_token = Column(String(40), nullable=True, unique=True)
    refresh_token = Column(String(40), nullable=True, unique=True)
    token_created_at = Column(DateTime)

    def __repr__(self):
        return f"<User username={self.username}>"