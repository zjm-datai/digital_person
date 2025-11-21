from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from models.engine import metadata

class Base(DeclarativeBase):
    metadata = metadata

# DelarativeBase 作用：
# 提供 ORM Declarative（声明式 Base）功能
# 所有模型继承它才能成为 ORM Model
# 承接 metadata

# 简单说：
# 👉 所有数据库表模型的祖先类（ORM 的核心基类）

# 给 Base 指定 metadata 的作用：
# 所有表共享 统一的命名规范（Constraint / Index 自动命名）
# 让 Alembic migration 更好用
# 保持团队风格一致
class TypeBase(MappedAsDataclass, DeclarativeBase):
    """
    This is for adding type, after all finished, rename to Base.
    """
    
    metadata = metadata

# MappedAsDataclass — 自动把 ORM 模型变成 dataclass

# 你在 TypeBase 里加了：

# class TypeBase(MappedAsDataclass, DeclarativeBase):
#     ...

# 这东西很强，它让模型变成 dataclass：

# ✔ 自动生成 __init__

# 原来 ORM 会这样的初始化：

# u = User(id=1, name="Jim")


# 但没有 dataclass 风格的类型检查和代码提示。

# 加上 MappedAsDataclass 后：

# 初始化会基于 Mapped[] 的类型自动生成参数

# 支持 dataclass 的默认值

# 支持 immutability（冻结 dataclass）

# 代码提示完美（IDE 强烈支持）

# 4. TypeBase 为啥要同时继承 MappedAsDataclass 和 DeclarativeBase？

# 因为 SQLAlchemy 官方推荐写法就是这样：

# 想让 ORM 模型作为 dataclass？
# 就继承 MappedAsDataclass + DeclarativeBase。

# 你的项目作者也照这个模式做了。