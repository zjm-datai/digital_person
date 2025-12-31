








import json
from typing import Generator, Mapping, Union

from flask.helpers import stream_with_context
from flask.wrappers import Response


def compact_generate_response(
    response: Union[Mapping, Generator]
) -> Response:
    print(response)
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