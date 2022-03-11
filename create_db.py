from database import Base, engine
from models import Mahasiswa

print("Creating database ...")

Base.metadata.create_all(engine)