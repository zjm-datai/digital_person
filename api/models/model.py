from datetime import datetime
from enum import StrEnum
import sqlalchemy as sa
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import TypeBase

class AppSetup(TypeBase):
    __tablename__ = "app_setups"
    __table_args__ = (sa.PrimaryKeyConstraint("version", name="app_setup_pkey"),)

    version: Mapped[str] = mapped_column(String(255), nullable=False)
    setup_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=func.current_timestamp(), init=False
    )

class AppType(StrEnum):
    PIFUKE = "pifuke"
    HUXIKE = "huxike"
    GANGCHANGKE = "gangchangke"

    GAOXUEYA = "gaoxueya"
    TANGNIAOBING = "tangniaobing"
    GAOXUEZHI = "gaoxuezhi"
    GAONIAOSUAN = "gaoniaosuan"
    FEIPANG = "feipang"
    DAXIE_ZONGHEZHENG = "daixie_zonghezheng"

