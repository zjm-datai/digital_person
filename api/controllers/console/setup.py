from flask import request
from flask_restx import Resource, fields
from pydantic import BaseModel, EmailStr, Field, field_validator

from controllers.console import console_ns
from libs.helper import extract_remote_ip
from libs.password import valid_password
from services.account_service import RegisterService

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"

class SetupRequestPayload(BaseModel):

    email: EmailStr = Field(..., description="Admin email address")
    name: str = Field(..., max_length=30, description="Admin name (max 30 characters)")
    password: str = Field(..., description="Admin password")
    language: str | None = Field(default=None, description="Admin language")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return valid_password(value)

console_ns.schema_model(
    SetupRequestPayload.__name__,
    SetupRequestPayload.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0),
)

@console_ns.route("/setup")
class SetupApi(Resource):

    @console_ns.doc("setup_system")
    @console_ns.doc(description="Initialize system setup with admin account")
    @console_ns.expect(console_ns.models[SetupRequestPayload.__name__])
    @console_ns.response(
        201, "Success", console_ns.model("SetupResponse", {"result": fields.String(description="Setup result")})
    )
    @console_ns.response(400, "Already setup or validation failed")
    def post(self):
        args = SetupRequestPayload.model_validate(console_ns.payload)

        RegisterService.setup(
            email=str(args.email),
            name=args.name,
            password=args.password,
            ip_address=extract_remote_ip(request),
            language=args.language,
        )

        return {
            "result": "success"
        }, 201
