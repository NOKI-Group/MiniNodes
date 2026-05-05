from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = "mininodes"
    db_password: str = "mininodes"
    db_name: str = "mininodes"
    db_host: str = "db"
    db_port: int = 5432

    secret_key: str = "changeme-in-production"

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
