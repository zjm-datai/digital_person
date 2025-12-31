

import logging
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from flask.app import Flask

from configs import app_config

logger = logging.getLogger(__name__)

connection_pool: ConnectionPool | None = None

def init_connection_pool() -> ConnectionPool | None:
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = ConnectionPool(
                app_config.SQLALCHEMY_DATABASE_URI,
                min_size=5,
                max_size=10,
                kwargs={
                    "autocommit": True,
                    "connect_timeout": 60,
                },
            )
        except Exception as e:
            logger.error("Connection pool 初始化失败: %s", e)
            raise
    else:
        logger.info("Connection pool 已存在")
    
    return connection_pool

def init_app(app: Flask):
    
    init_connection_pool()
        
    
    