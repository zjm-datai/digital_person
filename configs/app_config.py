


from pydantic_settings import SettingsConfigDict

from .middleware import MiddlewareConfig
from .features import FeaturesConfig
from .deploy import DeploymentConfig


class AppConfig(
    MiddlewareConfig,
    FeaturesConfig,
    DeploymentConfig
):
    
      
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )