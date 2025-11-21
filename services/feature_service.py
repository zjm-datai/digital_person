

from pydantic import BaseModel

from configs import app_config


class SystemFeatureModel(BaseModel):
    is_allow_register: bool = False
    is_email_setup: bool = False
    is_allow_create_workspace: bool = False


class FeatureService:

    @classmethod
    def get_system_features(cls) -> SystemFeatureModel:
        system_features = SystemFeatureModel()

        cls._fulfill_system_params_from_env(system_features)

        if app_config.ENTERPRIZE_ENABLED:
            pass

        return system_features

    @classmethod
    def _fulfill_system_params_from_env(cls, system_features: SystemFeatureModel):
        system_features.is_allow_register = app_config.ALLOW_REGISTER
        system_features.is_allow_create_workspace = app_config.ALLOW_CREATE_WORKSPACE
        system_features.is_email_setup = app_config.MAIL_TYPE is not None and app_config.MAIL_TYPE != ""
