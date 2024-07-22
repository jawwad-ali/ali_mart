from app import settings
from sqlmodel import create_engine,SQLModel
 
connection_string = str(settings.DATABASE_URL).replace(  
    "postgresql", "postgresql+psycopg" 
)   
  
# recycle connections after 5 minutes 
# to correspond with the compute scale down  
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)

# DB instance and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)