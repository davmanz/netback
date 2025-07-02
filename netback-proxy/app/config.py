import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DJANGO_API_PROTOCOL: str = os.getenv('DJANGO_API_PROTOCOL', 'http')
    DJANGO_API_URL: str = os.getenv('DJANGO_API_URL')
    DJANGO_API_PORT: int = int(os.getenv('DJANGO_API_PORT'))
    HOST: str = os.getenv('FASTAPI_PROXY_URL')
    PORT: int = int(os.getenv('FASTAPI_PROXY_PORT'))
    DEBUG: bool = os.getenv('FASTAPI_PROXY_URL', 'false').lower() == 'true'
    ALLOW_ORIGINS: list[str] = os.getenv('ALLOW_ORIGINS', '*').split(',')
    ALLOW_CREDENTIALS: bool = os.getenv('ALLOW_CREDENTIALS', 'true').lower() == 'true'
    ALLOW_METHODS: list[str] = os.getenv('ALLOW_METHODS', 'GET,POST,PUT,PATCH,DELETE,OPTIONS').split(',')
    ALLOW_HEADERS: list[str] = os.getenv('ALLOW_HEADERS', 'Content-Type,Authorization').split(',')

    @property
    def full_django_api_url(self) -> str:
        return f'{self.DJANGO_API_PROTOCOL}://{self.DJANGO_API_URL}:{self.DJANGO_API_PORT}/api'

settings = Settings()
