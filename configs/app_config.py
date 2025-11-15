


from pydantic_settings import SettingsConfigDict

from .middleware import MiddlewareConfig


class AppConfig(
    MiddlewareConfig,
):
    
      
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",

        # ignore extra attributes
        extra="ignore",
    )