
from pydantic import Field
from pydantic_settings import BaseSettings


class DeploymentConfig(BaseSettings):

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=False,
    )