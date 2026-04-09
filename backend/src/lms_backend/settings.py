from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(..., alias="NAME")
    debug: bool = Field(..., alias="DEBUG")
    address: str = Field(..., alias="ADDRESS")
    port: int = Field(..., alias="PORT")
    reload: bool = Field(..., alias="RELOAD")

    cors_origins: list[str] = Field(..., alias="CORS_ORIGINS")

    enable_interactions: bool = Field(..., alias="BACKEND_ENABLE_INTERACTIONS")
    enable_learners: bool = Field(..., alias="BACKEND_ENABLE_LEARNERS")

    autochecker_api_url: str = Field(..., alias="AUTOCHECKER_API_URL")
    autochecker_email: str = Field(..., alias="AUTOCHECKER_API_LOGIN")
    autochecker_password: str = Field(..., alias="AUTOCHECKER_API_PASSWORD")

    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(..., alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")

    jwt_secret: str = Field(..., alias="JWT_SECRET")


settings = Settings.model_validate({})
