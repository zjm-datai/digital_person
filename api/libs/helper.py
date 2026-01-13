
import json
from typing import Generator, Mapping, Union, cast

from flask.helpers import stream_with_context
from flask.wrappers import Response
from flask_restx import fields


def compact_generate_response(
    response: Union[Mapping, Generator]
) -> Response:

    if isinstance(response, dict):
        return Response(
            response=json.dumps(response),
            status=200, 
            mimetype="application/json"
        )
    else:
        def generate() -> Generator:
            yield from response
            
        return Response(
            stream_with_context(generate()), 
            status=200, mimetype="text/event-stream"
        )

def extract_remote_ip(request) -> str:
    if request.headers.get("CF-Connecting-IP"):
        return cast(str, request.headers.get("CF-Connecting-IP"))
    elif request.headers.getlist("X-Forwarded-For"):
        return cast(str, request.headers.getlist("X-Forwarded-For"))
    else:
        return cast(str, request.remote_addr)

class TimestampField(fields.Raw):
    def format(self, value) -> int:
        return int(value.timestamp())