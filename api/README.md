
http://127.0.0.1:5001/console/api/swagger-ui.html

```shell
uv run python -m flask db migrate -m "add message_kind field to message table"
```

```shell
uv run python -m flask db upgrade
```

```shell
uv run celery -A app.celery worker -l info
```

build image

```shell
docker build -t ningtang/consultation-api:1.0.0 .
```