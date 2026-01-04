
from flask_restx import Resource
from pydantic import BaseModel, Field
from werkzeug.exceptions import InternalServerError
from controllers.console import console_ns
from services.patient_service import PatientService

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"

class PatientQuery(BaseModel):
    opc_id: str = Field(..., description="OpcId of the patient")

def reg(cls: type[BaseModel]):
    console_ns.schema_model(cls.__name__, cls.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0))

reg(PatientQuery)

@console_ns.route('/patient_base')
class PatientBaseApi(Resource):

    @console_ns.expect(console_ns.models[PatientQuery.__name__])
    def post(self):
        args = PatientQuery.model_validate(console_ns.payload)
        opc_id = args.opc_id

        try:
            patient_base = PatientService.get_patient_base(opc_id)
        except Exception as e:
            raise InternalServerError() from e

        return patient_base

@console_ns.route('/patient_detail')
class PatientDetailApi(Resource):

    @console_ns.expect(console_ns.models[PatientQuery.__name__])
    def post(self):
        args = PatientQuery.model_validate(console_ns.payload)
        opc_id = args.opc_id
        try:
            patient_detail = PatientService.get_patient_detail(opc_id)
        except Exception as e:
            raise InternalServerError() from e

        return patient_detail