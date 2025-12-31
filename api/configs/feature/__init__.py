
from pydantic import (   
    Field,
    PositiveInt,
    PositiveFloat,
    
    AliasChoices,
    
    computed_field
)

from pydantic_settings import BaseSettings

class SecurityConfig(BaseSettings):
    SECRET_KEY: str = Field(
        description="Secret key for secure session cookie signing."
                    "Make sure you are changing this key for your deployment with a strong key."
                    "Generate a strong key using `openssl rand -base64 42` or set via the `SECRET_KEY` environment variable.",
        default="",
    )
    LOGIN_DISABLED: bool = Field(
        description="Whether to disable login checks",
        default=False,
    )
    ADMIN_API_KEY_ENABLE: bool = Field(
        description="Whether to enable admin api key for authentication",
        default=False,
    )

    ADMIN_API_KEY: str | None = Field(
        description="admin api key for authentication",
        default=None,
    )

class EndpointConfig(BaseSettings):
    """
    Configuration for various application endpoints and URLs
    """

    CONSOLE_API_URL: str = Field(
        description="Base URL for the console API,"
        "used for login authentication callback or notion integration callbacks",
        default="",
    )

    CONSOLE_WEB_URL: str = Field(
        description="Base URL for the console web interface, used for frontend references and CORS configuration",
        default="",
    )

class HttpConfig(BaseSettings):
    """
    HTTP-related configurations for the application
    """

    COOKIE_DOMAIN: str = Field(
        description="Explicit cookie domain for console/service cookies when sharing across subdomains",
        default="",
    )

class LoggingConfig(BaseSettings):
    """
    Configuration for application logging
    """

    LOG_LEVEL: str = Field(
        description="Logging level, default to INFO. Set to ERROR for production environments.",
        default="INFO",
    )

    LOG_FILE: str | None = Field(
        description="File path for log output.",
        default=None,
    )

    LOG_FILE_MAX_SIZE: PositiveInt = Field(
        description="Maximum file size for file rotation retention, the unit is megabytes (MB)",
        default=20,
    )

    LOG_FILE_BACKUP_COUNT: PositiveInt = Field(
        description="Maximum file backup count file rotation retention",
        default=5,
    )

    LOG_FORMAT: str = Field(
        description="Format string for log messages",
        default=(
            "%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] "
            "[%(filename)s:%(lineno)d] %(trace_id)s - %(message)s"
        ),
    )

    LOG_DATEFORMAT: str | None = Field(
        description="Date format string for log timestamps",
        default=None,
    )

    LOG_TZ: str | None = Field(
        description="Timezone for log timestamps (e.g., 'America/New_York')",
        default="UTC",
    )
    
class HttpConfig(BaseSettings):
    """
    HTTP-related configurations for the application
    """

    COOKIE_DOMAIN: str = Field(
        description="Explicit cookie domain for console/service cookies when sharing across subdomains",
        default="",
    )

    API_COMPRESSION_ENABLED: bool = Field(
        description="Enable or disable gzip compression for HTTP responses",
        default=False,
    )

    inner_CONSOLE_CORS_ALLOW_ORIGINS: str = Field(
        description="Comma-separated list of allowed origins for CORS in the console",
        validation_alias=AliasChoices("CONSOLE_CORS_ALLOW_ORIGINS", "CONSOLE_WEB_URL"),
        default="",
    )

    @computed_field
    def CONSOLE_CORS_ALLOW_ORIGINS(self) -> list[str]:
        return self.inner_CONSOLE_CORS_ALLOW_ORIGINS.split(",")

    inner_WEB_API_CORS_ALLOW_ORIGINS: str = Field(
        description="",
        validation_alias=AliasChoices("WEB_API_CORS_ALLOW_ORIGINS"),
        default="*",
    )

    @computed_field
    def WEB_API_CORS_ALLOW_ORIGINS(self) -> list[str]:
        return self.inner_WEB_API_CORS_ALLOW_ORIGINS.split(",")

    HTTP_REQUEST_MAX_CONNECT_TIMEOUT: int = Field(
        ge=1, description="Maximum connection timeout in seconds for HTTP requests", default=10
    )

    HTTP_REQUEST_MAX_READ_TIMEOUT: int = Field(
        ge=1, description="Maximum read timeout in seconds for HTTP requests", default=600
    )

    HTTP_REQUEST_MAX_WRITE_TIMEOUT: int = Field(
        ge=1, description="Maximum write timeout in seconds for HTTP requests", default=600
    )

    HTTP_REQUEST_NODE_MAX_BINARY_SIZE: PositiveInt = Field(
        description="Maximum allowed size in bytes for binary data in HTTP requests",
        default=10 * 1024 * 1024,
    )

    HTTP_REQUEST_NODE_MAX_TEXT_SIZE: PositiveInt = Field(
        description="Maximum allowed size in bytes for text data in HTTP requests",
        default=1 * 1024 * 1024,
    )

    HTTP_REQUEST_NODE_SSL_VERIFY: bool = Field(
        description="Enable or disable SSL verification for HTTP requests",
        default=True,
    )

    SSRF_DEFAULT_MAX_RETRIES: PositiveInt = Field(
        description="Maximum number of retries for network requests (SSRF)",
        default=3,
    )

    SSRF_PROXY_ALL_URL: str | None = Field(
        description="Proxy URL for HTTP or HTTPS requests to prevent Server-Side Request Forgery (SSRF)",
        default=None,
    )

    SSRF_PROXY_HTTP_URL: str | None = Field(
        description="Proxy URL for HTTP requests to prevent Server-Side Request Forgery (SSRF)",
        default=None,
    )

    SSRF_PROXY_HTTPS_URL: str | None = Field(
        description="Proxy URL for HTTPS requests to prevent Server-Side Request Forgery (SSRF)",
        default=None,
    )

    SSRF_DEFAULT_TIME_OUT: PositiveFloat = Field(
        description="The default timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_DEFAULT_CONNECT_TIME_OUT: PositiveFloat = Field(
        description="The default connect timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_DEFAULT_READ_TIME_OUT: PositiveFloat = Field(
        description="The default read timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_DEFAULT_WRITE_TIME_OUT: PositiveFloat = Field(
        description="The default write timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_POOL_MAX_CONNECTIONS: PositiveInt = Field(
        description="Maximum number of concurrent connections for the SSRF HTTP client",
        default=100,
    )

    SSRF_POOL_MAX_KEEPALIVE_CONNECTIONS: PositiveInt = Field(
        description="Maximum number of persistent keep-alive connections for the SSRF HTTP client",
        default=20,
    )

    SSRF_POOL_KEEPALIVE_EXPIRY: PositiveFloat | None = Field(
        description="Keep-alive expiry in seconds for idle SSRF connections (set to None to disable)",
        default=5.0,
    )

    RESPECT_XFORWARD_HEADERS_ENABLED: bool = Field(
        description="Enable handling of X-Forwarded-For, X-Forwarded-Proto, and X-Forwarded-Port headers"
        " when the app is behind a single trusted reverse proxy.",
        default=False,
    )

class AuthConfig(BaseSettings):
    """
    Configuration for authentication and OAuth
    """

    ACCESS_TOKEN_EXPIRE_MINUTES: PositiveInt = Field(
        description="Expiration time for access tokens in minutes",
        default=60,
    )

    REFRESH_TOKEN_EXPIRE_DAYS: PositiveFloat = Field(
        description="Expiration time for refresh tokens in days",
        default=30,
    )
    
class SwaggerUIConfig(BaseSettings):
    SWAGGER_UI_ENABLED: bool = Field(
        description="Whether to enable Swagger UI in api module",
        default=True,
    )

    SWAGGER_UI_PATH: str = Field(
        description="Swagger UI page path in api module",
        default="/swagger-ui.html",
    )
    
class FeatureConfig(
    HttpConfig,
    LoggingConfig,
    SwaggerUIConfig,
    SecurityConfig
):
    pass