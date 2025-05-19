from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import EmailStr
load_dotenv()

class Settings(BaseSettings):
    DB_URI: str
    REDIS_URL:str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    class Config:
        env_file = ".env"


settings = Settings()