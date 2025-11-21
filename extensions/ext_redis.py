import ssl
from typing import Any, Union

import redis
from redis import Connection, SSLConnection
from flask import Flask

from configs import app_config

redis_client = None

def _get_ssl_configuration() -> tuple[type[Connection, SSLConnection], dict[str, Any]]:
    """Get SSL configuration for Redis connection."""

    if app_config['REDIS_USE_SSL']:
        return Connection, {}
    cert_reqs_map = {
        "CERT_NONE": ssl.CERT_NONE,
        "CERT_OPTIONAL": ssl.CERT_OPTIONAL,
        "CERT_REQUIRED": ssl.CERT_REQUIRED,
    }
    ssl_cert_reqs = cert_reqs_map.get(app_config.REDIS_SSL_CERT_REQS, ssl.CERT_NONE)

    ssl_kwargs = {
        "ssl_cert_reqs": ssl_cert_reqs,
        "ssl_ca_certs": app_config.REDIS_SSL_CA_CERTS,
        "ssl_certfile": app_config.REDIS_SSL_CERTFILE,
        "ssl_keyfile": app_config.REDIS_SSL_KEYFILE,
    }

    return SSLConnection, ssl_kwargs


def _get_base_redis_params() -> dict[str, Any]:
    """Get base Redis connection parameters."""

    return {
        "username": app_config.REDIS_USERNAME,
        "password": app_config.REDIS_PASSWORD or None,
        "db": app_config.REDIS_DB,
        "encoding": "utf-8",
        "encoding_errors": "strict",
        "decode_responses": False,
        "protocol": app_config.REDIS_SERIALIZATION_PROTOCOL,
        # "cache_config": _get_cache_configuration(),
    }

def _create_standalone_client(redis_params: dict[str, Any]) -> Union[redis.Redis, redis.RedisCluster]:
    """Create standalone Redis client."""

    connection_class, ssl_kwargs = _get_ssl_configuration()

    redis_params.update(
        {
            "host": app_config.REDIS_HOST,
            "port": app_config.REDIS_PORT,
            "connection_class": connection_class,
        }
    )

    if ssl_kwargs:
        redis_params.update(ssl_kwargs)

    pool = redis.ConnectionPool(**redis_params)
    client: redis.Redis = redis.Redis(connection_pool=pool)
    return client

def init_app(app: Flask):
    """Initialize Redis client and attach it to the app."""

    global redis_client

    if app_config.REDIS_USE_SENTINEL:
        pass
    elif app_config.REDIS_USE_CLUSTER:
        pass
    else:
        redis_params = _get_base_redis_params()
        redis_client = _create_standalone_client(redis_params)

    app.extensions["redis"] = redis_client