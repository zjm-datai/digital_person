import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

from models.base import TypeBase

"""
当 Alembic 的 env.py 执行 from models.base import TypeBase 时，流程变成：

1. Python 找到 models 包 → 执行 models/__init__.py

2. 在 __init__.py 里执行 from .account import Account, ...

3. 于是 models.account 被导入，里面定义的 Account 等模型类被执行

4. 这些模型类是继承 TypeBase（或者 Base）的，比如类似这样：

# models/account.py
class Account(TypeBase):
    __tablename__ = "account"
    ...

5. 定义 Account 这一刻，SQLAlchemy 会把它对应的表对象注册到 TypeBase.metadata 里面

6. env.py 里的：
def get_metadata():
    return TypeBase.metadata
就能拿到包含 Account 等表的 metadata，flask db migrate 自然就能检测出迁移了。

## 那么之前为什么不行？

在你还没有 models/__init__.py 时，情况是这样的：

models 目录存在，但没有 __init__.py

在 Python 3 里，这会被当成一个 namespace package，是一个空壳包，导入它不会执行任何代码

from models.base import TypeBase 时：

只会导入 models.base 这个模块

不会自动去导入 models.account

结果就是：

TypeBase 自己被加载了，但没有任何继承它的模型类被定义

TypeBase.metadata 里是空的或不完整的

Alembic 对比 metadata 和数据库结构时，看不到 Account 这些表 ⇒ 不生成迁移
"""

def get_metadata():
    return TypeBase.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    include_object 是 Alembic 的 过滤钩子函数（callback），
    用于控制 哪些数据库对象参与自动迁移（autogenerate）。

    当你运行：

    flask db migrate

    Alebmic 会比较 models 与数据库的差异，自动生成迁移脚本。
    include_object 就是用于决定 某个对象是否需要包含进自动迁移过程。
    也就是说，它是一个“过滤器”。

    object 当前检查的数据库对象（列、表、外键、约束…）
    name 对象名称
    type_ 对象类型（例如 "table", "column", "foreign_key_constraint"）
    reflected 是否来自数据库反射
    compare_to 用于比较的另一对象（可能来自 model）
    """

    # 所有外键（ForeignKey Constraint）都不参与自动迁移。
    if type_ == "foreign_key_constraint":
        return False
    else:
        return True

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            # TODO
            # 仔细查看逻辑
            include_object=include_object,
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
