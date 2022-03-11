from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://nirjjxkloynuxg:6de13031d5f69cc4675577a113ed8d19554ac49e9800d895fe54bc65a59d2669@ec2-18-234-17-166.compute-1.amazonaws.com:5432/df0ddn816h7hnf",
    echo=True
)

Base = declarative_base()

SessionLocal = sessionmaker(bind = engine)