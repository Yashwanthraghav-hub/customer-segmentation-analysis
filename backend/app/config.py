from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "customer-segmentation-api"
    cors_origins: str = "http://localhost:5173,http://localhost:4173"
    max_upload_mb: int = 10
    require_auth: bool = False
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]


settings = Settings()
