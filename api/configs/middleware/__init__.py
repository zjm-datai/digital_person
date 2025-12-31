
import os
from typing import Any, Literal
from urllib.parse import parse_qsl, quote_plus

from pydantic import Field, NonNegativeInt, PositiveInt, computed_field, SecretStr
from pydantic_settings import BaseSettings


class StorageConfig(BaseSettings):
    STORAGE_TYPE: Literal[
        "minio",
        "local",
    ] = Field(
        description="Type of storage to use.",
        default="minio",
    )

    STORAGE_LOCAL_PATH: str = Field(
        description="Local storage path, used when STORAGE_TYPE is 'local'.",
        default="storage",
        deprecated=True,
    )

class MinioStoreConfig(BaseSettings):
    MINIO_ENDPOINT: str = Field(
        ...,  # 必须提供的配置
        description="MinIO 服务端点",
    )
    MINIO_ACCESS_KEY: str = Field(
        ...,
        description="MinIO 访问密钥",
    )
    MINIO_SECRET_KEY: str = Field(
        ...,
        description="MinIO 密钥",
    )
    MINIO_SECURE: bool = Field(
        True,
        description="是否使用 HTTPS",
    )
    MINIO_BUCKET_NAME: str = Field(
        ...,
        description="MinIO 存储桶名称",
    )
    MINIO_UPLOAD_FOLDER: str = Field(
        "downloads",
        description="MinIO 下载到本地的默认目录",
    )
    MINIO_PATH: str = Field(
        "",
        description="MinIO 中的路径",
    )

class LLMConfig(BaseSettings):
    LLM_MODEL: str = Field(
        default="gpt-4o",
        description="Name of the LLM to use (e.g. 'gpt-4o', 'gpt-3.5-turbo')"
    )
    DEFAULT_LLM_TEMPERATURE: float = Field(
        default=0.5,
        description="Sampling temperature for the LLM",
        ge=0.0,
        le=2.0
    )
    LLM_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="API key for accessing the LLM service"
    )
    LLM_BASE_URL: str = Field(
        default="http://127.0.0.1:4000/v1",
        description="Base URL for the LLM HTTP API"
    )
    MAX_TOKENS: NonNegativeInt = Field(
        default=2048,
        description="Maximum number of tokens to generate per call",
        ge=0
    )
    MAX_LLM_CALL_RETRIES: NonNegativeInt = Field(
        default=2,
        description="Maximum retry times when LLM call failed"
    )
    
class DatabaseConfig(BaseSettings):
    # Database type selector
    DB_TYPE: Literal["postgresql", "mysql", "oceanbase"] = Field(
        description="Database type to use. OceanBase is MySQL-compatible.",
        default="postgresql",
    )

    DB_HOST: str = Field(
        description="Hostname or IP address of the database server.",
        default="localhost",
    )

    DB_PORT: PositiveInt = Field(
        description="Port number for database connection.",
        default=5432,
    )

    DB_USERNAME: str = Field(
        description="Username for database authentication.",
        default="postgres",
    )

    DB_PASSWORD: str = Field(
        description="Password for database authentication.",
        default="",
    )

    DB_DATABASE: str = Field(
        description="Name of the database to connect to.",
        default="dify",
    )

    DB_CHARSET: str = Field(
        description="Character set for database connection.",
        default="",
    )

    DB_EXTRAS: str = Field(
        description="Additional database connection parameters. Example: 'keepalives_idle=60&keepalives=1'",
        default="",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI_SCHEME(self) -> str:
        return "postgresql" if self.DB_TYPE == "postgresql" else "mysql+pymysql"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        db_extras = (
            f"{self.DB_EXTRAS}&client_encoding={self.DB_CHARSET}" if self.DB_CHARSET else self.DB_EXTRAS
        ).strip("&")
        db_extras = f"?{db_extras}" if db_extras else ""
        return (
            f"{self.SQLALCHEMY_DATABASE_URI_SCHEME}://"
            f"{quote_plus(self.DB_USERNAME)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
            f"{db_extras}"
        )

    SQLALCHEMY_POOL_SIZE: NonNegativeInt = Field(
        description="Maximum number of database connections in the pool.",
        default=30,
    )

    SQLALCHEMY_MAX_OVERFLOW: NonNegativeInt = Field(
        description="Maximum number of connections that can be created beyond the pool_size.",
        default=10,
    )

    SQLALCHEMY_POOL_RECYCLE: NonNegativeInt = Field(
        description="Number of seconds after which a connection is automatically recycled.",
        default=3600,
    )

    SQLALCHEMY_POOL_USE_LIFO: bool = Field(
        description="If True, SQLAlchemy will use last-in-first-out way to retrieve connections from pool.",
        default=False,
    )

    SQLALCHEMY_POOL_PRE_PING: bool = Field(
        description="If True, enables connection pool pre-ping feature to check connections.",
        default=False,
    )

    SQLALCHEMY_ECHO: bool | str = Field(
        description="If True, SQLAlchemy will log all SQL statements.",
        default=False,
    )

    SQLALCHEMY_POOL_TIMEOUT: NonNegativeInt = Field(
        description="Number of seconds to wait for a connection from the pool before raising a timeout error.",
        default=30,
    )

    RETRIEVAL_SERVICE_EXECUTORS: NonNegativeInt = Field(
        description="Number of processes for the retrieval service, default to CPU cores.",
        default=os.cpu_count() or 1,
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict[str, Any]:
        # Parse DB_EXTRAS for 'options'
        db_extras_dict = dict(parse_qsl(self.DB_EXTRAS))
        options = db_extras_dict.get("options", "")
        connect_args = {}
        # Use the dynamic SQLALCHEMY_DATABASE_URI_SCHEME property
        if self.SQLALCHEMY_DATABASE_URI_SCHEME.startswith("postgresql"):
            timezone_opt = "-c timezone=UTC"
            if options:
                merged_options = f"{options} {timezone_opt}"
            else:
                merged_options = timezone_opt
            connect_args = {"options": merged_options}

        return {
            "pool_size": self.SQLALCHEMY_POOL_SIZE,
            "max_overflow": self.SQLALCHEMY_MAX_OVERFLOW,
            "pool_recycle": self.SQLALCHEMY_POOL_RECYCLE,
            "pool_pre_ping": self.SQLALCHEMY_POOL_PRE_PING,
            "connect_args": connect_args,
            "pool_use_lifo": self.SQLALCHEMY_POOL_USE_LIFO,
            "pool_reset_on_return": None,
            "pool_timeout": self.SQLALCHEMY_POOL_TIMEOUT,
        }
        
class CeleryConfig(DatabaseConfig):
    CELERY_BACKEND: str = Field(
        description="Backend for Celery task results. Options: 'database', 'redis', 'rabbitmq'.",
        default="redis",
    )

    CELERY_BROKER_URL: str | None = Field(
        description="URL of the message broker for Celery tasks.",
        default=None,
    )
    
    @computed_field
    def CELERY_RESULT_BACKEND(self) -> str | None:
        if self.CELERY_BACKEND in ("database", "rabbitmq"):
            return f"db+{self.SQLALCHEMY_DATABASE_URI}"
        elif self.CELERY_BACKEND == "redis":
            return self.CELERY_BROKER_URL
        else:
            return None
    
class MiddlewareConfig(
    CeleryConfig,
    # configs of storage and storage providers
    StorageConfig,
    LLMConfig
):
    pass