
from flask import Flask

def init_app(app: Flask):

    import flask_migrate

    from extensions.ext_database import db

    flask_migrate.Migrate(app, db)

"""

将 Flask 应用与 SQLAlchemy 实例绑定到 Flask-Migrate
app：你的 Flask 应用实例。
db：由 Flask-SQLAlchemy 提供的数据库对象（通常是 SQLAlchemy() 的实例）。

Migrate(app, db) 会：
自动读取 app.config['SQLALCHEMY_DATABASE_URI']；
初始化底层的 Alembic 迁移引擎；
注册一系列 CLI 命令（如 flask db init, flask db migrate, flask db upgrade 等）。

当你第一次运行 flask db init（前提是已经执行了 Migrate(app, db)），Flask-Migrate 会：

在项目根目录下生成一个 migrations/ 文件夹；
里面包含 Alembic 的配置文件（alembic.ini、env.py 等）；
后续所有 migrate 和 upgrade 操作都依赖这个环境。

有了它：

开发时：flask db migrate -m "add user email" 自动生成变更脚本；
部署时：flask db upgrade 一键升级生产库结构。
"""