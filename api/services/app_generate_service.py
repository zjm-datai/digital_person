

from enum import StrEnum

from core.graph_apps.daixie_zonghezheng_app_generator import DaixieZonghezhengAppGenerator
from core.graph_apps.feipang_app_generator import FeipangAppGenerator
from core.graph_apps.gangchangke_app_generator import GangChangAppGenerator
from core.graph_apps.gaoniaosuan_app_generator import GaoniaosuanAppGenerator
from core.graph_apps.gaoxueya_app_generator import GaoxueyaAppGenerator
from core.graph_apps.gaoxuezhi_app_generator import GaoxuezhiAppGenerator
from core.graph_apps.huxike_app_generator import HuxikeAppGenerator
from core.graph_apps.pifuke_app_generator import PifukeAppGenerator
from core.graph_apps.tangniaobing_app_generator import TangniaobingAppGenerator
from models.model import AppType


class AppGenerateService:
    
    @staticmethod
    def generate(
        app_type: str, conversation_id: str, message: str, streaming: bool = False
    ):
        try:
            if app_type == AppType.PIFUKE:
                return PifukeAppGenerator.convert_to_event_stream(
                    PifukeAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.HUXIKE:
                return HuxikeAppGenerator.convert_to_event_stream(
                    HuxikeAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.GANGCHANGKE:
                return GangChangAppGenerator.convert_to_event_stream(
                    GangChangAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.GAOXUEYA:
                return GaoxueyaAppGenerator.convert_to_event_stream(
                    GaoxueyaAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.FEIPANG:
                return FeipangAppGenerator.convert_to_event_stream(
                    FeipangAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.GAONIAOSUAN:
                return GaoniaosuanAppGenerator.convert_to_event_stream(
                    GaoniaosuanAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.TANGNIAOBING:
                return TangniaobingAppGenerator.convert_to_event_stream(
                    TangniaobingAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.GAOXUEZHI:
                return GaoxuezhiAppGenerator.convert_to_event_stream(
                    GaoxuezhiAppGenerator().generate(message, conversation_id, streaming)
                )
            elif app_type == AppType.DAXIE_ZONGHEZHENG:
                return DaixieZonghezhengAppGenerator.convert_to_event_stream(
                    DaixieZonghezhengAppGenerator().generate(message, conversation_id, streaming)
                )
            else:
                raise ValueError(f"Unsupported app_type: {app_type}")
        except Exception as e:
            raise
        finally:
            pass