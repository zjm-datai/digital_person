from flask_restx import fields

from libs.helper import TimestampField

account_fields = {
    "id": fields.String,
    "name": fields.String,
    "email": fields.String,
    "is_password_set": fields.Boolean,
    "interface_language": fields.String,
    "timezone": fields.String,
    "last_login_at": TimestampField,
    "last_login_ip": fields.String,
    "created_at": TimestampField,
}