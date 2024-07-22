from starlette.config import Config
from starlette.datastructures import Secret
 
try: 
    config = Config(".env")
except FileNotFoundError: 
    config = Config()   
 
DATABASE_URL:str = config("DATABASE_URL", cast=Secret)