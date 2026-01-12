from database import engine
from database.models import Base

print("init")
Base.metadata.create_all(bind=engine)
print("done")