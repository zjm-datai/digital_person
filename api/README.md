
http://127.0.0.1:5001/console/api/swagger-ui.html

```shell
uv run python -m flask db migrate -m "add message_kind field to message table"
```

```shell
uv run python -m flask db upgrade
```