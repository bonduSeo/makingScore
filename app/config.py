from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MakingScore Wrapper"
    output_dir: str = "outputs"

    openai_api_key: str | None = None

    # Optional OAuth scaffold (can be OpenAI or compatible OIDC provider)
    oauth_enabled: bool = False
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    oauth_authorize_url: str = "https://auth.openai.com/oauth/authorize"
    oauth_token_url: str = "https://auth.openai.com/oauth/token"
    oauth_userinfo_url: str = "https://api.openai.com/v1/me"
    oauth_redirect_uri: str = "http://localhost:8000/auth/callback"


settings = Settings()
