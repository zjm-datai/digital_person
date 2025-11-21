
import logging

import gevent
from flask import Flask
from sqlalchemy import Pool, event

from models.engine import db

logger = logging.getLogger(__name__)


# Global flag to avoid duplicate registration of event listener
_gevent_compatibility_setup: bool = False

"""
1. 为什么需要 reset ？

在 sqlalchemy 中，数据库连接来自连接池 Pool
每当我们执行完一个请求之后，sqlalchemy 会把连接放回连接池，放回之前就会进行 reset 操作

reset 的作用在于：
- 清理上一个请求留下的状态
- 取消未提交的事务
- rollback 任何脏状态
- 让连接保持干净可复用

也就是说 reset 是连接池保证连接可重复使用的必要步骤。
如果不 reset，会把上一次请求的事务带到下一次，严重错误。

2. 为什么 Flask + gevent 会用到协程（greenlet）？

如果你直接用 Flask（同步），是不会有 gevent 的。
但是 Gunicorn、某些部署模式会使用 gevent worker

gunicorn app:app -k gevent

或者你手动使用：

gevent.monkey.patch_all()

这会把 socket、thread、time、ssl 等模块全部变成异步协程版本（greenlet）。

此时：

每个 HTTP 请求不再是 OS 线程

而是一个 greenlet 协程

协程之间会在 I/O 时切换

因此：

你以为 Flask 是同步的，但在 gevent 环境里，数据库操作已经在协程里执行了。

3. SQLAlchemy 在 gevent 环境里会出现的问题（核心原因）

问题核心：SQLAlchemy 的 reset() 是同步执行的

SQLAlchemy 在 reset 时会：

connection.rollback()

但如果此时正处于 gevent 的 callback 中（例如 I/O 切换点），
greenlet scheduler 不允许执行 I/O 或阻塞操作，很可能出现：

🔥典型报错：
- AssertionError: Unexpected switch
- greenlet.error: cannot switch to a different thread
- psycopg2.InterfaceError: connection already closed
- reset 中断导致连接池 “脏连接”

这些错误会让 SQLAlchemy 连接池的连接：

- 无法正常回收
- 留在错误状态
- 下一次使用时报各种奇怪的问题


为什么 gevent callback 中 rollback 会出现问题？

gevent loop libev 在执行 callback 的时候：
- 不允许 greenlet 切换
- 不允许产生 I/O block
- 不能执行耗时操作

rollback 本质上是数据库操作，会触发 I/O，导致：
callback 里执行 rollback，greenlet 会在错误位置发生切换，引发异常。
"""

def _safe_rollback(connection):
    """Safely rollback database connection.

    Args:
        connection: Database connection object
    """
    try:
        connection.rollback()
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to rollback connection")


def _setup_gevent_compatibility():
    """Setup gevent compatibility for SQLAlchemy."""
    global _gevent_compatibility_setup

    if _gevent_compatibility_setup:
        return
    
    @event.listens_for(Pool, "reset")
    def _safe_reset(dbapi_connection, connection_record, reset_state):
        if reset_state.terminate_only:
            return
        
        # Safe rollback for conection
        try:
            hub = gevent.get_hub()
            if hasattr(hub, "loop") and getattr(hub.loop, "in_callback", False):
                gevent.spawn_later(0, lambda: _safe_rollback(dbapi_connection))
            else:
                _safe_rollback(dbapi_connection)
        except (AttributeError, ImportError):
            _safe_rollback(dbapi_connection)

    _gevent_compatibility_setup = True


def init_app(app: Flask):
    db.init_app(app)
    # _setup_gevent_compatibility()

"""
init_app() 会做以下几件事：

绑定应用上下文：将 db 实例与传入的 Flask app 关联起来。
设置配置：读取 app.config 中与 SQLAlchemy 相关的配置项（如 SQLALCHEMY_DATABASE_URI、SQLALCHEMY_TRACK_MODIFICATIONS 等）。
注册 teardown handler：在请求结束时自动清理数据库会话（session）。
启用 Flask 的应用上下文支持：使得在视图函数或命令行中可以使用 db.session、db.create_all() 等功能。
注意：db.init_app(app) 只是“准备”好数据库连接和 ORM 工具，并不会主动去连接数据库服务器，更不会创建数据库文件或表结构。

对于 SQLite：
数据库文件（如 example.db）会在首次实际访问数据库时（比如执行 db.create_all() 或发起一个查询）被自动创建。
但 init_app() 本身不会触发这个行为。
对于 MySQL / PostgreSQL 等：
数据库（schema）必须预先手动创建（例如通过 CREATE DATABASE mydb;）。
Flask-SQLAlchemy 不会自动创建数据库本身，只负责在已有数据库中创建表。

如何创建数据表？
通常在应用初始化后，手动调用：

with app.app_context():
    db.create_all()

这会在已存在的数据库中根据你定义的模型（继承自 db.Model 的类）创建对应的表。

⚠️ 注意：db.create_all() 不会创建数据库（database），只会创建表（tables）。数据库必须已经存在且可连接。
"""