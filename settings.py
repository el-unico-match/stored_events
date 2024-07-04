from typing import List
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    disable_db:bool=False
	
    log_filename:str='stored_events.log'
    NOTSET:int=0
    DEBUG:int=10
    INFO:int=20
    WARNING:int=30
    ERROR:int=40
    CRITICAL:int=50	
    logging_level:int=DEBUG
	
    DOCKER_DOMAIN:str='stored_events_postgres'
    LOCAL_DOMAIN:str='localhost'
    db_domain:str = LOCAL_DOMAIN
    db_port:int = 5000
    db_host:str=db_domain+":"+str(db_port)
    local_db_name:str='local'
    remote_db_name:str='remote'	
    db_name:str=local_db_name
    db_credentials:str=''
    database_url:str=''
	
    apikey_value:str=''
    apikey_status:str=''
    apikey_activate_endpoint:str=''
    apikey_whitelist:List[str]=[]
    apikey_whitelist_endpoint:str=''

    LIKE_LIMITS:int=2
    SUPERLIKE_LIMITS:int=4

    notification_server_key:str=''
	
    model_config = SettingsConfigDict(env_file=("dev.env",".env"))	

def loadSettings():
     settings=Settings()
     settings.database_url=f"postgresql://{settings.db_credentials}@{settings.db_domain}:{settings.db_port}/{settings.db_name}"
     return settings

settings=loadSettings()
